type Item = {
  name: string
  url: string
}

const BASE = 'https://cardfight.fandom.com'
const BOOSTER_PATTERN = /(^VG[\w\-\:\s]+)|\bVG-BT\d+\b/i

/**
 * Normaliza URL
 */
const normalizeUrl = (href: string) =>
  href.startsWith('http') ? href : new URL(href, BASE).toString()

/**
 * Extrae boosters desde tablas `.wikitable`
 */
const extractFromTables = (doc: Document): Item[] =>
  Array.from(doc.querySelectorAll('table.wikitable'))
    .flatMap(table =>
      Array.from(table.querySelectorAll('tr')).flatMap(row => {
        const cells = Array.from(row.querySelectorAll('td'))
        if (!cells.length) return []

        const first = cells[0]
        const a = first.querySelector('a[href]')

        if (a && a.textContent?.trim()) {
          return [{
            name: a.textContent.trim(),
            url: normalizeUrl(a.getAttribute('href') || '')
          }]
        }

        const text = first.textContent?.trim()
        return text ? [{ name: text, url: BASE }] : []
      })
    )

/**
 * Extrae boosters desde listas `<li>`
 */
const extractFromListItems = (doc: Document): Item[] =>
  Array.from((doc.querySelector('.mw-parser-output') || doc.body).querySelectorAll('li'))
    .flatMap(li => {
      const a = li.querySelector('a[href]')
      if (!a) return []

      const title = a.textContent?.trim()
      const href = a.getAttribute('href') || ''

      return title && href.includes('/wiki/')
        ? [{ name: title, url: normalizeUrl(href) }]
        : []
    })

/**
 * Extrae boosters desde anchors (fallback agresivo)
 */
const extractFromAnchors = (doc: Document): Item[] =>
  Array.from(doc.querySelectorAll('a[href]'))
    .map(a => ({
      title: a.textContent?.trim(),
      href: a.getAttribute('href') || ''
    }))
    .filter(t =>
      t.title &&
      t.href &&
      t.href.includes('/wiki/') &&
      BOOSTER_PATTERN.test(t.title)
    )
    .map(t => ({
      name: t.title as string,
      url: normalizeUrl(t.href)
    }))

/**
 * Elimina duplicados por URL
 */
const dedupeResults = (items: Item[]): Item[] => {
  const map = new Map<string, Item>()
  items.forEach(it => {
    if (!map.has(it.url)) {
      map.set(it.url, it)
    }
  })
  return Array.from(map.values())
}

/**
 * EXTRA
 * Limpia nombres raros tipo "[VG-BT02] Name"
 */
const normalizeName = (name: string) =>
  name.replace(/\s+/g, ' ').trim()

/**
 * Función principal
 */
export const extractBoosters = (html: string): Item[] => {
  const doc = new DOMParser().parseFromString(html, 'text/html')

  const results = [
    ...extractFromTables(doc),
    ...extractFromListItems(doc),
    ...extractFromAnchors(doc),
  ]

  if (results.length === 0) {
    console.warn('⚠️ No se encontraron boosters, posible cambio en la web')
  }

  return dedupeResults(results).map(b => ({
    name: normalizeName(b.name),
    url: b.url
  }))
}