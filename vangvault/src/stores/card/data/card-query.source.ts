import type { CardQuerySource } from './card-query.types'

import {
  searchCardsByWikiMetadata,
  searchCardsByWikiText,
} from '../helpers/card-text-search.api'

/**
 * ADAPTADOR ACTUAL: CARD LIST NORMALIZADA + MEDIAWIKI
 * --------------------------------------------------
 * - Type y Trigger se resuelven con `cardKind` / `triggerKind`, ya obtenidos
 *   de la Card List.
 * - Clan y texto libre usan el índice de MediaWiki cuando hace falta.
 */
export const wikiCardQuerySource: CardQuerySource = {
  searchText: searchCardsByWikiText,
  searchMetadata: searchCardsByWikiMetadata,
}

/**
 * Único punto donde la aplicación elige el origen de las consultas.
 *
 * Este contrato separa ya los filtros de la vista. Cuando exista el índice se
 * podrá crear un adaptador HTTP con la misma respuesta. Para evitar además
 * cargar por scraping una generación completa habrá que sustituir también el
 * cargador de ámbitos de `card.store.ts`, tal como explica
 * `docs/DATA_SOURCE_MIGRATION.md`.
 */
export const cardQuerySource: CardQuerySource =
  wikiCardQuerySource
