import type {
  CardEntry,
  CardKind,
  TriggerKind,
} from '@/models/card-entry.model'

/**
 * Filtros que no pueden resolverse únicamente con Grade/Nation de la vista.
 *
 * Se mantienen separados del componente Vue para que cualquier origen de
 * datos —wiki ahora, endpoint de Mongo en el futuro— reciba la misma petición.
 */
export type CardMetadataFilters = {
  clan: string
  type: CardKind | 'all'
  trigger: TriggerKind | 'all'
}

/**
 * Resultado común de cualquier fuente de consultas.
 *
 * Se devuelven ids porque las cartas completas ya están en la store. Así la
 * vista solo tiene que intersectar el resultado con su ámbito actual.
 */
export type CardQueryResult = {
  cardIds: Set<string>
  wasTruncated: boolean
}

/**
 * Contrato que debe cumplir un origen de búsquedas de cartas.
 *
 * La vista no sabe si la implementación usa MediaWiki, una API serverless o
 * Mongo. Solo conoce estas dos operaciones y su forma de respuesta.
 */
export interface CardQuerySource {
  searchText(
    cards: CardEntry[],
    searchText: string
  ): Promise<CardQueryResult>

  searchMetadata(
    cards: CardEntry[],
    filters: CardMetadataFilters
  ): Promise<CardQueryResult>
}
