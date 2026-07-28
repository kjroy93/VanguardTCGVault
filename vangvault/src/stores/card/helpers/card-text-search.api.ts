import type { CardEntry } from '@/models/card-entry.model'

import {
  fetchWikiApiJson,
  getWikiPageTitleFromUrl,
} from '@/services/wiki/wiki.client'

type WikiSearchResponse = {
  continue?: {
    continue?: string
    sroffset?: number
  }

  query?: {
    search?: Array<{
      title?: string
    }>
  }
}

export type WikiTextSearchResult = {
  cardIds: Set<string>
  wasTruncated: boolean
}

export type WikiAdvancedFilters = {
  clan: string
  type: string
  trigger: string
}

type CachedSearchResult = {
  pageTitleKeys: string[]
  wasTruncated: boolean
}

const SEARCH_PAGE_SIZE = 50
const MAX_SEARCH_REQUESTS = 20

/**
 * Memoria temporal de búsquedas ya realizadas.
 *
 * Evita repetir la misma consulta a Fandom mientras la aplicación siga abierta.
 */
const cachedSearches = new Map<
  string,
  CachedSearchResult
>()

/** Normaliza texto para compararlo sin diferencias de formato. */
const normalizeText = (value: string): string =>
  value
    .replaceAll('_', ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()

/**
 * Permite escribir varios términos separados por `;`.
 *
 * Los términos vacíos se descartan.
 */
const getSearchTerms = (value: string): string[] =>
  value
    .split(';')
    .map(term => term.trim())
    .filter(Boolean)

/**
 * Obtiene una clave comparable a partir de la URL de la ficha.
 *
 * Si la URL no pertenece a la wiki, devuelve una cadena vacía en vez de romper
 * toda la búsqueda.
 */
const getCardPageTitleKey = (
  card: CardEntry
): string => {
  try {
    return normalizeText(
      getWikiPageTitleFromUrl(card.wikiUrl)
    )
  } catch {
    return ''
  }
}

/**
 * Construye el texto que ya conocemos localmente, sin hacer fetch.
 *
 * Así nombre, número, nación o rareza pueden coincidir inmediatamente.
 */
const getLocalSearchText = (
  card: CardEntry
): string =>
  normalizeText([
    card.cardNumber,
    card.name,
    card.nation,
    card.rarity,
    card.setCode,
    card.generation,
    card.listType,
  ]
    .filter(Boolean)
    .join(' '))

/**
 * Pregunta al buscador de MediaWiki qué páginas contienen una consulta.
 *
 * Sigue la paginación hasta terminar o alcanzar el límite de seguridad y
 * conserva el resultado en caché.
 */
const getWikiTitleKeysForQuery = async (
  query: string
): Promise<CachedSearchResult> => {
  const cacheKey = query.trim().toLowerCase()

  const cached = cachedSearches.get(cacheKey)

  /** Una consulta repetida puede resolverse sin volver a usar la red. */
  if (cached) {
    return cached
  }

  const pageTitleKeys = new Set<string>()

  let continuationParams: Record<string, string> = {}
  let wasTruncated = false

  for (
    let requestIndex = 0;
    requestIndex < MAX_SEARCH_REQUESTS;
    requestIndex += 1
  ) {
    /**
     * `continuationParams` contiene el cursor que MediaWiki devuelve para
     * solicitar la página siguiente de resultados.
     */
    const json = await fetchWikiApiJson<WikiSearchResponse>({
      action: 'query',
      list: 'search',
      srsearch: query,
      srwhat: 'text',
      srnamespace: '0',
      srlimit: String(SEARCH_PAGE_SIZE),
      ...continuationParams,
    })

    for (const result of json.query?.search ?? []) {
      if (!result.title) {
        continue
      }

      pageTitleKeys.add(
        normalizeText(result.title)
      )
    }

    const next = json.continue

    if (!next) {
      break
    }

    if (requestIndex === MAX_SEARCH_REQUESTS - 1) {
      wasTruncated = true
      break
    }

    continuationParams = {}

    if (next.continue) {
      continuationParams.continue = next.continue
    }

    if (next.sroffset !== undefined) {
      continuationParams.sroffset = String(
        next.sroffset
      )
    }
  }

  const result: CachedSearchResult = {
    pageTitleKeys: [...pageTitleKeys],
    wasTruncated,
  }

  cachedSearches.set(cacheKey, result)

  return result
}

/**
 * Cruza los títulos encontrados por MediaWiki con las cartas del ámbito actual
 * y devuelve únicamente sus ids.
 */
const getMatchingCardIds = (
  cards: CardEntry[],
  pageTitleKeys: Set<string>
): Set<string> => {
  const matchingIds = new Set<string>()

  for (const card of cards) {
    const pageTitleKey = getCardPageTitleKey(card)

    if (
      pageTitleKey &&
      pageTitleKeys.has(pageTitleKey)
    ) {
      matchingIds.add(card.id)
    }
  }

  return matchingIds
}

/**
 * Busca texto libre en fichas de carta.
 * Los términos separados por ";" se intersectan.
 *
 * Para cada término une coincidencias locales y coincidencias del contenido de
 * la wiki. Después exige que la carta haya coincidido con todos los términos.
 */
export const searchCardsByWikiText = async (
  cards: CardEntry[],
  searchText: string
): Promise<WikiTextSearchResult> => {
  const terms = getSearchTerms(searchText)

  if (terms.length === 0) {
    return {
      cardIds: new Set(cards.map(card => card.id)),
      wasTruncated: false,
    }
  }

  let matchingCardIds = new Set(
    cards.map(card => card.id)
  )

  let wasTruncated = false

  for (const rawTerm of terms) {
    const normalizedTerm = normalizeText(rawTerm)

    const wikiResult =
      await getWikiTitleKeysForQuery(rawTerm)

    wasTruncated =
      wasTruncated || wikiResult.wasTruncated

    const wikiTitleKeys = new Set(
      wikiResult.pageTitleKeys
    )

    const matchingIdsForTerm = new Set<string>()

    for (const card of cards) {
      const matchesLocalData =
        getLocalSearchText(card).includes(
          normalizedTerm
        )

      const pageTitleKey = getCardPageTitleKey(card)

      const matchesWikiText =
        pageTitleKey !== '' &&
        wikiTitleKeys.has(pageTitleKey)

      if (matchesLocalData || matchesWikiText) {
        matchingIdsForTerm.add(card.id)
      }
    }

    matchingCardIds = new Set(
      [...matchingCardIds].filter(cardId =>
        matchingIdsForTerm.has(cardId)
      )
    )

    if (matchingCardIds.size === 0) {
      break
    }
  }

  return {
    cardIds: matchingCardIds,
    wasTruncated,
  }
}

/**
 * Traduce el botón de tipo a la frase que debe buscar MediaWiki.
 */
const getTypeQuery = (
  type: string
): string | undefined => {
  switch (type) {
    case 'unit':
      return '"Normal Unit"'

    case 'trigger':
      return '"Trigger Unit"'

    case 'order':
      return '"Normal Order"'

    case 'blitz':
      return '"Blitz Order"'

    default:
      return undefined
  }
}

/**
 * Traduce el botón de trigger a la frase que debe buscar MediaWiki.
 */
const getTriggerQuery = (
  trigger: string
): string | undefined => {
  switch (trigger) {
    case 'draw':
      return '"Trigger Effect" "Draw"'

    case 'critical':
      return '"Trigger Effect" "Critical"'

    case 'front':
      return '"Trigger Effect" "Front"'

    case 'heal':
      return '"Trigger Effect" "Heal"'

    case 'over':
      return '"Trigger Effect" "Over"'

    default:
      return undefined
  }
}

/**
 * Busca metadatos de ficha sin pedir el HTML de cada carta.
 *
 * Ejemplos:
 * - Trigger → "Trigger Unit"
 * - Critical → "Trigger Effect" "Critical"
 * - Murakumo → "Clan" "Murakumo"
 *
 * Cada filtro produce una consulta. Los resultados se intersectan para que una
 * carta tenga que cumplir todos los filtros activos.
 */
export const searchCardsByWikiMetadata = async (
  cards: CardEntry[],
  filters: WikiAdvancedFilters
): Promise<WikiTextSearchResult> => {
  const queries: string[] = []

  if (filters.clan !== 'all') {
    queries.push(
      `"Clan" "${filters.clan}"`
    )
  }

  const typeQuery = getTypeQuery(filters.type)

  if (typeQuery) {
    queries.push(typeQuery)
  }

  const triggerQuery = getTriggerQuery(
    filters.trigger
  )

  if (triggerQuery) {
    queries.push(triggerQuery)
  }

  if (queries.length === 0) {
    return {
      cardIds: new Set(cards.map(card => card.id)),
      wasTruncated: false,
    }
  }

  let matchingCardIds = new Set(
    cards.map(card => card.id)
  )

  let wasTruncated = false

  for (const query of queries) {
    const wikiResult =
      await getWikiTitleKeysForQuery(query)

    wasTruncated =
      wasTruncated || wikiResult.wasTruncated

    const matchingIds = getMatchingCardIds(
      cards,
      new Set(wikiResult.pageTitleKeys)
    )

    matchingCardIds = new Set(
      [...matchingCardIds].filter(cardId =>
        matchingIds.has(cardId)
      )
    )

    if (matchingCardIds.size === 0) {
      break
    }
  }

  return {
    cardIds: matchingCardIds,
    wasTruncated,
  }
}
