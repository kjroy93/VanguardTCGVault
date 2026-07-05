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

export const fetchWikiApiJson = async <T>(
  params: Record<string, string>
): Promise<T> => {
  const fandomRequestUrl = buildApiUrl(
    FANDOM_API_URL,
    params
  )

  return trySources<T>([
    () => fetchJson<T>(buildApiUrl('/wiki-api', params)),
    () => fetchJson<T>(ALL_ORIGINS(fandomRequestUrl)),
  ])
}

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
  return fetchWikiPageHtmlByTitle(
    getWikiPageTitleFromUrl(wikiUrl)
  )
}