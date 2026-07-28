import type { CardEntry } from '@/models/card-entry.model'
import type {
  CardMetadataFilters,
  CardQueryResult,
} from '@/stores/card/data/card-query.types'

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
): Promise<CardQueryResult> => {
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
 * Convierte un nombre de categoría en una consulta exacta para MediaWiki.
 *
 * `incategory` evita que, por ejemplo, una unidad normal coincida solo porque
 * su efecto menciona la palabra "Critical".
 */
const getCategoryQuery = (
  categoryName: string
): string =>
  `incategory:"${categoryName.replaceAll('"', '\\"')}"`

/**
 * Aplica los campos categóricos que ya fueron normalizados desde Card List.
 *
 * Esta parte no hace fetch. Si falta el dato, la carta no se incluye: es más
 * seguro mostrar menos resultados que inventar una coincidencia por texto.
 */
const filterByNormalizedMetadata = (
  cards: CardEntry[],
  filters: CardMetadataFilters
): CardEntry[] =>
  cards.filter(card => {
    const matchesType =
      filters.type === 'all' ||
      card.cardKind === filters.type

    const matchesTrigger =
      filters.trigger === 'all' ||
      card.triggerKind === filters.trigger

    return matchesType && matchesTrigger
  })

/**
 * Busca metadatos sin pedir el HTML individual de cada carta.
 *
 * Type y Trigger salen de la columna Type de Card List. Clan aún no aparece en
 * todas esas tablas, así que se consulta como categoría exacta y se intersecta
 * con las cartas ya filtradas.
 */
export const searchCardsByWikiMetadata = async (
  cards: CardEntry[],
  filters: CardMetadataFilters
): Promise<CardQueryResult> => {
  const locallyFilteredCards =
    filterByNormalizedMetadata(cards, filters)

  if (filters.clan === 'all') {
    return {
      cardIds: new Set(
        locallyFilteredCards.map(card => card.id)
      ),
      wasTruncated: false,
    }
  }

  if (locallyFilteredCards.length === 0) {
    return {
      cardIds: new Set(),
      wasTruncated: false,
    }
  }

  const wikiResult = await getWikiTitleKeysForQuery(
    getCategoryQuery(filters.clan)
  )

  return {
    cardIds: getMatchingCardIds(
      locallyFilteredCards,
      new Set(wikiResult.pageTitleKeys)
    ),
    wasTruncated: wikiResult.wasTruncated,
  }
}
