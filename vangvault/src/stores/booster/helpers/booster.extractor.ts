export type BoosterSourceItem = {
  name: string
  url: string
}

const BASE = 'https://cardfight.fandom.com'
const BOOSTER_PATTERN =
  /\bVGE?(?:-[A-Z0-9]+)+\b|^(?:P&V|DZ|D|V|G)?\s*Special Series\s+\d+\b/i

/**
 * Decide si un texto parece el nombre de un producto Vanguard.
 *
 * Sirve para no introducir en el catálogo enlaces del menú, categorías,
 * páginas de ayuda u otros enlaces que también aparecen en el HTML.
 */
const isBoosterTitle = (
  value?: string | null
): value is string =>
  Boolean(value && BOOSTER_PATTERN.test(value.trim()))

/**
 * NORMALIZACIÓN 1: convierte enlaces relativos de la wiki en URL absolutas.
 */
const normalizeUrl = (href: string) =>
  href.startsWith('http') ? href : new URL(href, BASE).toString()

/**
 * EXTRACCIÓN: busca productos en tablas `.wikitable`.
 */
const extractFromTables = (doc: Document): BoosterSourceItem[] =>
  Array.from(doc.querySelectorAll('table.wikitable'))
    .flatMap(table =>
      Array.from(table.querySelectorAll('tr')).flatMap(row => {
        const cells = Array.from(row.querySelectorAll('td'))
        if (!cells.length) return []

        const first = cells[0]
        const a = first.querySelector('a[href]')
        const href = a?.getAttribute('href') || ''

        if (
          a &&
          isBoosterTitle(a.textContent) &&
          href.includes('/wiki/')
        ) {
          return [{
            name: a.textContent.trim(),
            url: normalizeUrl(href)
          }]
        }

        /** Sin enlace no habría una página desde la que cargar cartas. */
        return []
      })
    )

/**
 * EXTRACCIÓN: busca productos en listas `<li>`.
 * El filtro evita confundir la navegación lateral y las categorías con sets.
 */
const extractFromListItems = (doc: Document): BoosterSourceItem[] =>
  Array.from((doc.querySelector('.mw-parser-output') || doc.body).querySelectorAll('li'))
    .flatMap(li => {
      const a = li.querySelector('a[href]')
      if (!a) return []

      const title = a.textContent?.trim()
      const href = a.getAttribute('href') || ''

      return isBoosterTitle(title) && href.includes('/wiki/')
        ? [{ name: title, url: normalizeUrl(href) }]
        : []
    })

/**
 * EXTRACCIÓN: último recurso para páginas cuyo contenido no usa tabla o lista.
 */
const extractFromAnchors = (doc: Document): BoosterSourceItem[] =>
  Array.from(doc.querySelectorAll('a[href]'))
    .map(a => ({
      title: a.textContent?.trim(),
      href: a.getAttribute('href') || ''
    }))
    .filter(t =>
      isBoosterTitle(t.title) &&
      t.href &&
      t.href.includes('/wiki/')
    )
    .map(t => ({
      name: t.title as string,
      url: normalizeUrl(t.href)
    }))

/**
 * NORMALIZACIÓN 2: elimina duplicados por página real de la wiki.
 * `URL` también evita que el SS presente en la lista y la categoría salga dos
 * veces. Conservamos el primer nombre, normalmente el código VGE/VG más útil.
 */
const dedupeResults = (
  items: BoosterSourceItem[]
): BoosterSourceItem[] => {
  const map = new Map<string, BoosterSourceItem>()

  items.forEach(it => {
    /**
     * Dos enlaces pueden escribir el mismo carácter de manera diferente
     * (`:` o `%3A`). Por eso comparamos la ruta ya decodificada y no la URL
     * literal.
     */
    const url = new URL(it.url)
    const pageKey = decodeURIComponent(url.pathname)
      .replace(/\/+$/, '')
      .toLowerCase()

    if (!map.has(pageKey)) {
      map.set(pageKey, it)
    }
  })

  return Array.from(map.values())
}

/**
 * NORMALIZACIÓN 3: deja espacios y saltos de línea en una forma estable.
 */
const normalizeName = (name: string) =>
  name.replace(/\s+/g, ' ').trim()

/**
 * HTML DE UNA FUENTE -> `{ name, url }[]`
 */
export const extractBoosters = (
  html: string
): BoosterSourceItem[] => {
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

/**
 * HTML DE TODAS LAS FUENTES -> CATÁLOGO ÚNICO
 *
 * Aquí se mezclan la lista de boosters, la lista histórica de SS y la
 * categoría actual. El parser posterior convertirá cada par en `BoosterSet`.
 */
export const extractBoostersFromPages = (
  htmlPages: string[]
): BoosterSourceItem[] =>
  dedupeResults(
    htmlPages.flatMap(html => extractBoosters(html))
  )

/**
 * Une varios catálogos y elimina las páginas repetidas.
 *
 * El orden importa: se conservan primero los datos obtenidos de la wiki y el
 * catálogo local solo completa aquello que no llegó por red.
 */
export const mergeBoosterItems = (
  ...catalogs: BoosterSourceItem[][]
): BoosterSourceItem[] =>
  dedupeResults(catalogs.flat())
