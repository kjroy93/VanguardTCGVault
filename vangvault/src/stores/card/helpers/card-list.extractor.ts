const WIKI_BASE_URL = 'https://cardfight.fandom.com'
const CARD_NUMBER_PATTERN =
  /\b[A-Z][A-Z0-9-]*\d[A-Z0-9-]*\/[A-Z0-9-]*\d[A-Z0-9-]*\b/i

export type ScrapedCardListRow = {
  cardNumber: string
  name: string
  wikiUrl: string
  grade?: string
  nation?: string
  listType?: string
  rarity?: string
}

/** Elimina saltos, espacios repetidos y espacios de los extremos. */
const cleanText = (value?: string | null): string =>
  (value ?? '')
    .replace(/\s+/g, ' ')
    .trim()

/**
 * Prepara el texto de una cabecera para compararlo sin depender de mayúsculas
 * o signos como el punto de `Card No.`.
 */
const normalizeHeader = (value: string): string =>
  cleanText(value)
    .toLowerCase()
    .replace(/[^\w]+/g, ' ')
    .trim()

/** Convierte un enlace relativo de Fandom en una URL completa. */
const normalizeWikiUrl = (href: string): string =>
  href.startsWith('http')
    ? href
    : new URL(href, WIKI_BASE_URL).toString()

/**
 * Busca qué posición ocupa una columna.
 *
 * Acepta varios nombres porque la wiki puede escribir `Card No`,
 * `Card Number`, `Name` o `Card Name`.
 */
const getColumnIndex = (
  headers: string[],
  acceptedNames: string[]
): number => {
  return headers.findIndex(header =>
    acceptedNames.some(
      accepted =>
        header === accepted ||
        header.startsWith(`${accepted} `)
    )
  )
}

/** Obtiene únicamente las celdas directas de una fila, sean `<th>` o `<td>`. */
const getRowCells = (
  row: HTMLTableRowElement
): HTMLTableCellElement[] =>
  Array.from(row.children).filter(
    (cell): cell is HTMLTableCellElement =>
      cell.matches('th, td')
  )

/** Comprueba si un texto tiene forma de número de carta Vanguard. */
const isCardNumber = (value?: string | null): boolean =>
  CARD_NUMBER_PATTERN.test(cleanText(value))

/**
 * Encuentra la fila que contiene los nombres de las columnas.
 *
 * No exige `<th>` porque algunas páginas construyen sus cabeceras con `<td>`.
 */
const findHeaderRow = (
  table: HTMLTableElement
): HTMLTableRowElement | undefined =>
  Array.from(table.querySelectorAll('tr')).find(row => {
    const headers = getRowCells(row).map(cell =>
      normalizeHeader(cell.textContent ?? '')
    )

    return (
      getColumnIndex(headers, [
        'card no',
        'card number',
      ]) !== -1 &&
      getColumnIndex(headers, [
        'name',
        'card name',
      ]) !== -1
    )
  })

/**
 * Reconoce una fila de datos por dos señales: contiene un número de carta y
 * algún enlace a una página de la wiki.
 */
const rowLooksLikeCard = (
  row: HTMLTableRowElement
): boolean => {
  const cells = getRowCells(row)

  return (
    cells.some(cell => isCardNumber(cell.textContent)) &&
    cells.some(
      cell =>
        cell.querySelector('a[href*="/wiki/"]') !==
        null
    )
  )
}

/**
 * Decide si una tabla es una Card List.
 *
 * Primero busca cabeceras claras. Si no existen, exige al menos dos filas que
 * parezcan cartas para no confundir una ficha informativa con el listado.
 */
const tableLooksLikeCardList = (
  table: HTMLTableElement
): boolean => {
  if (findHeaderRow(table)) {
    return true
  }

  /**
   * Algunas tablas usan `<td>` o no conservan un encabezado semántico. Dos
   * filas con "número + enlace de carta" son una señal más estable que
   * depender de la etiqueta HTML concreta.
   */
  return Array.from(table.querySelectorAll('tr'))
    .filter(rowLooksLikeCard)
    .length >= 2
}

/**
 * Busca la tabla situada bajo el título `Card List`.
 *
 * Si la estructura de la página ha cambiado, recorre después todas las tablas
 * como alternativa.
 */
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
  /**
   * NORMALIZACIÓN DE CARD LIST
   * --------------------------
   * Entrada: HTML del set seleccionado.
   * Salida: filas simples con número, nombre, URL y metadatos básicos.
   *
   * Acepta encabezados creados con `<th>` o `<td>` y, como último recurso,
   * deduce las columnas por el patrón del número y el enlace de la carta.
   */
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

  const headerRow = findHeaderRow(table)
  const headers = headerRow
    ? getRowCells(headerRow).map(cell =>
        normalizeHeader(cell.textContent ?? '')
      )
    : []

  const cardNumberIndex = getColumnIndex(headers, [
    'card no',
    'card number',
  ])

  const nameIndex = getColumnIndex(headers, [
    'name',
    'card name',
  ])
  const gradeIndex = getColumnIndex(headers, ['grade'])
  const nationIndex = getColumnIndex(headers, ['nation'])
  const typeIndex = getColumnIndex(headers, ['type'])
  const rarityIndex = getColumnIndex(headers, ['rarity'])

  const seen = new Set<string>()

  return rows.flatMap(row => {
    if (row === headerRow) return []

    const cells = getRowCells(row)

    if (!cells.length) return []

    const inferredCardNumberIndex = cells.findIndex(cell =>
      isCardNumber(cell.textContent)
    )

    /**
     * Preferimos la posición indicada por la cabecera. Si esa posición no
     * contiene un número válido, usamos la posición deducida en esta fila.
     */
    const effectiveCardNumberIndex =
      cardNumberIndex !== -1 &&
      isCardNumber(cells[cardNumberIndex]?.textContent)
        ? cardNumberIndex
        : inferredCardNumberIndex

    const cardNumber = cleanText(
      cells[effectiveCardNumberIndex]?.textContent
    )

    const inferredNameIndex = cells.findIndex(
      (cell, index) => {
        if (index === effectiveCardNumberIndex) {
          return false
        }

        const link = cell.querySelector(
          'a[href*="/wiki/"]'
        )

        return (
          link !== null &&
          !isCardNumber(link.textContent)
        )
      }
    )

    /**
     * La celda de nombre debe contener un enlace que no sea el propio número.
     * Así evitamos escoger por error la nación u otra columna enlazada.
     */
    const effectiveNameIndex =
      nameIndex !== -1 &&
      cells[nameIndex]?.querySelector(
        'a[href*="/wiki/"]'
      )
        ? nameIndex
        : inferredNameIndex

    const nameCell = cells[effectiveNameIndex]
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
