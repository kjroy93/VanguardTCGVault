type WikiParseResponse = {
  parse?: {
    text?: string
  }
}

const FANDOM_API_URL = 'https://cardfight.fandom.com/api.php'
const WIKI_PATH_PREFIX = '/wiki/'

const ALL_ORIGINS = (target: string) =>
  `https://api.allorigins.win/raw?url=${encodeURIComponent(target)}`

const fetchJson = async <T>(path: string): Promise<T> => {
  const response = await fetch(path)

  if (!response.ok) {
    throw new Error(`Wiki API error: ${response.status}`)
  }

  return response.json() as Promise<T>
}

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

const buildParseUrl = (
  apiBaseUrl: string,
  pageTitle: string
) => {
  const params = new URLSearchParams({
    action: 'parse',
    page: pageTitle,
    prop: 'text',
    formatversion: '2',
    format: 'json',
  })

  return `${apiBaseUrl}?${params.toString()}`
}

const getPageTitleFromWikiUrl = (wikiUrl: string): string => {
  const url = new URL(wikiUrl)
  const path = url.pathname

  if (!path.startsWith(WIKI_PATH_PREFIX)) {
    throw new Error(`URL de wiki no válida: ${wikiUrl}`)
  }

  return decodeURIComponent(
    path.slice(WIKI_PATH_PREFIX.length)
  ).replaceAll('_', ' ')
}

export const fetchWikiPageHtmlByTitle = async (
  pageTitle: string
): Promise<string> => {
  const fandomRequestUrl = buildParseUrl(
    FANDOM_API_URL,
    pageTitle
  )

  const json = await trySources<WikiParseResponse>([
    () => fetchJson(buildParseUrl('/wiki-api', pageTitle)),
    () => fetchJson(ALL_ORIGINS(fandomRequestUrl)),
  ])

  const html = json.parse?.text

  if (!html) {
    throw new Error('La wiki respondió sin HTML parseable')
  }

  return html
}

export const fetchWikiPageHtml = (
  wikiUrl: string
): Promise<string> => {
  const pageTitle = getPageTitleFromWikiUrl(wikiUrl)

  return fetchWikiPageHtmlByTitle(pageTitle)
}