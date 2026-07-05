const WIKI_BASE_URL = 'https://cardfight.fandom.com'

export type ScrapedCardListRow = {
  cardNumber: string
  name: string
  wikiUrl: string
  grade?: string
  nation?: string
  listType?: string
  rarity?: string
}

const cleanText = (value?: string | null): string =>
  (value ?? '')
    .replace(/\s+/g, ' ')
    .trim()

const normalizeHeader = (value: string): string =>
  cleanText(value)
    .toLowerCase()
    .replace(/[^\w]+/g, ' ')
    .trim()

const normalizeWikiUrl = (href: string): string =>
  href.startsWith('http')
    ? href
    : new URL(href, WIKI_BASE_URL).toString()

const getColumnIndex = (
  headers: string[],
  acceptedNames: string[]
): number => {
  return headers.findIndex(header =>
    acceptedNames.includes(header)
  )
}

const tableLooksLikeCardList = (
  table: HTMLTableElement
): boolean => {
  const headerRow = Array.from(
    table.querySelectorAll('tr')
  ).find(row => row.querySelectorAll('th').length > 0)

  if (!headerRow) return false

  const headers = Array.from(
    headerRow.querySelectorAll('th')
  ).map(cell => normalizeHeader(cell.textContent ?? ''))

  return (
    getColumnIndex(headers, ['card no', 'card number']) !== -1 &&
    getColumnIndex(headers, ['name']) !== -1
  )
}

const findCardListTable = (
  doc: Document
): HTMLTableElement | null => {
  const headings = Array.from(
    doc.querySelectorAll('h2, h3, h4')
  )

  const cardListHeading = headings.find(heading =>
    cleanText(heading.textContent).toLowerCase() === 'card list'
  )

  if (cardListHeading) {
    let current = cardListHeading.nextElementSibling

    while (current) {
      if (/^H[2-4]$/.test(current.tagName)) {
        break
      }

      const table = current.matches('table')
        ? current
        : current.querySelector('table')

      if (
        table instanceof HTMLTableElement &&
        tableLooksLikeCardList(table)
      ) {
        return table
      }

      current = current.nextElementSibling
    }
  }

  return (
    Array.from(doc.querySelectorAll('table'))
      .find(table => tableLooksLikeCardList(table)) ??
    null
  )
}

export const extractCardListRowsFromHtml = (
  html: string
): ScrapedCardListRow[] => {
  const doc = new DOMParser().parseFromString(
    html,
    'text/html'
  )

  const table = findCardListTable(doc)

  if (!table) {
    throw new Error(
      'No se encontró una tabla Card List reconocible en este booster'
    )
  }

  const rows = Array.from(table.querySelectorAll('tr'))

  const headerRow = rows.find(
    row => row.querySelectorAll('th').length > 0
  )

  if (!headerRow) {
    throw new Error('La Card List no tiene encabezados reconocibles')
  }

  const headers = Array.from(
    headerRow.querySelectorAll('th')
  ).map(cell => normalizeHeader(cell.textContent ?? ''))

  const cardNumberIndex = getColumnIndex(headers, [
    'card no',
    'card number',
  ])

  const nameIndex = getColumnIndex(headers, ['name'])
  const gradeIndex = getColumnIndex(headers, ['grade'])
  const nationIndex = getColumnIndex(headers, ['nation'])
  const typeIndex = getColumnIndex(headers, ['type'])
  const rarityIndex = getColumnIndex(headers, ['rarity'])

  const seen = new Set<string>()

  return rows.flatMap(row => {
    const cells = Array.from(row.querySelectorAll('td'))

    if (!cells.length) return []

    const cardNumber = cleanText(
      cells[cardNumberIndex]?.textContent
    )

    const nameCell = cells[nameIndex]
    const link = nameCell?.querySelector('a[href*="/wiki/"]')

    const name = cleanText(link?.textContent ?? nameCell?.textContent)
    const href = link?.getAttribute('href')

    if (!cardNumber || !name || !href) {
      return []
    }

    const wikiUrl = normalizeWikiUrl(href)
    const uniqueKey = `${cardNumber}|${wikiUrl}`

    if (seen.has(uniqueKey)) {
      return []
    }

    seen.add(uniqueKey)

    return [{
      cardNumber,
      name,
      wikiUrl,
      grade: cleanText(cells[gradeIndex]?.textContent) || undefined,
      nation: cleanText(cells[nationIndex]?.textContent) || undefined,
      listType: cleanText(cells[typeIndex]?.textContent) || undefined,
      rarity: cleanText(cells[rarityIndex]?.textContent) || undefined,
    }]
  })
}