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

const cachedSearches = new Map<
  string,
  CachedSearchResult
>()

const normalizeText = (value: string): string =>
  value
    .replaceAll('_', ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()

const getSearchTerms = (value: string): string[] =>
  value
    .split(';')
    .map(term => term.trim())
    .filter(Boolean)

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

const getWikiTitleKeysForQuery = async (
  query: string
): Promise<CachedSearchResult> => {
  const cacheKey = query.trim().toLowerCase()

  const cached = cachedSearches.get(cacheKey)

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