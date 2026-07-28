type WikiParseResponse = {
  parse?: {
    text?: string
  }
}

const FANDOM_API_URL = 'https://cardfight.fandom.com/api.php'
const WIKI_PATH_PREFIX = '/wiki/'
const FETCH_TIMEOUT_MS = 10_000

/**
 * Este es el único nivel que hace el `fetch` HTTP genérico.
 *
 * Prueba tres caminos porque Fandom puede bloquear temporalmente alguno:
 * 1. La API directa desde el navegador, usando el CORS oficial de MediaWiki.
 * 2. `/wiki-api`, que Vite redirige a Fandom durante el desarrollo.
 * 3. AllOrigins como último recurso.
 *
 * Los stores no conocen estos detalles: solo piden HTML o JSON a este archivo.
 */
const ALL_ORIGINS = (target: string) =>
  `https://api.allorigins.win/raw?url=${encodeURIComponent(target)}`

/**
 * Ejecuta un `fetch`, comprueba el código HTTP y convierte la respuesta a JSON.
 *
 * El genérico `T` describe la forma que espera el fichero que hizo la llamada.
 */
const fetchJson = async <T>(path: string): Promise<T> => {
  const controller = new AbortController()

  const timeoutId = setTimeout(
    () => controller.abort(),
    FETCH_TIMEOUT_MS
  )

  let response: Response

  try {
    response = await fetch(path, {
      signal: controller.signal,
    })
  } finally {
    clearTimeout(timeoutId)
  }

  if (!response.ok) {
    throw new Error(`Wiki API error: ${response.status}`)
  }

  return response.json() as Promise<T>
}

/**
 * Prueba varias maneras de obtener el mismo dato, una detrás de otra.
 *
 * Devuelve la primera que funciona. Si fallan todas, relanza el último error
 * para que la store o la vista puedan decidir cómo mostrarlo.
 */
const trySources = async <T>(
  sources: Array<() => Promise<T>>
): Promise<T> => {
  let lastError: unknown

  for (const source of sources) {
    try {
      return await source()
    } catch (error) {
      lastError = error
    }
  }

  throw lastError ?? new Error('No se pudo obtener respuesta de la wiki')
}

/** Construye una URL de MediaWiki codificando correctamente sus parámetros. */
const buildApiUrl = (
  apiBaseUrl: string,
  params: Record<string, string>
): string => {
  const searchParams = new URLSearchParams({
    format: 'json',
    formatversion: '2',
    ...params,
  })

  return `${apiBaseUrl}?${searchParams.toString()}`
}

/**
 * Punto de entrada para cualquier petición JSON a MediaWiki.
 *
 * Los helpers de stores indican la acción y parámetros; esta función decide
 * por qué ruta HTTP intentar obtenerlos.
 */
export const fetchWikiApiJson = async <T>(
  params: Record<string, string>
): Promise<T> => {
  const fandomRequestUrl = buildApiUrl(
    FANDOM_API_URL,
    {
      origin: '*',
      ...params,
    }
  )

  return trySources<T>([
    () => fetchJson<T>(fandomRequestUrl),
    () => fetchJson<T>(buildApiUrl('/wiki-api', params)),
    () => fetchJson<T>(ALL_ORIGINS(fandomRequestUrl)),
  ])
}

/**
 * Convierte una URL visible de Fandom en el título que entiende su API.
 * Ejemplo: `/wiki/DZ_Special_Series_16:_...` -> `DZ Special Series 16: ...`.
 */
export const getWikiPageTitleFromUrl = (
  wikiUrl: string
): string => {
  const url = new URL(wikiUrl)

  if (!url.pathname.startsWith(WIKI_PATH_PREFIX)) {
    throw new Error(`URL de wiki no válida: ${wikiUrl}`)
  }

  return decodeURIComponent(
    url.pathname.slice(WIKI_PATH_PREFIX.length)
  ).replaceAll('_', ' ')
}

/**
 * Pide a MediaWiki el HTML ya renderizado de una página.
 * Todavía no extrae sets ni cartas: esa normalización se hace en los
 * extractores de `stores/booster` y `stores/card`.
 */
export const fetchWikiPageHtmlByTitle = async (
  pageTitle: string
): Promise<string> => {
  const json = await fetchWikiApiJson<WikiParseResponse>({
    action: 'parse',
    page: pageTitle,
    prop: 'text',
  })

  const html = json.parse?.text

  if (!html) {
    throw new Error('La wiki respondió sin HTML parseable')
  }

  return html
}

export const fetchWikiPageHtml = (
  wikiUrl: string
): Promise<string> => {
  /**
   * Las cartas y sets guardan una URL visible. Antes de consultar la API se
   * convierte esa URL a su título interno.
   */
  return fetchWikiPageHtmlByTitle(
    getWikiPageTitleFromUrl(wikiUrl)
  )
}
