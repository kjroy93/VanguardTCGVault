import type {
  CardKind,
  TriggerKind,
} from '@/models/card-entry.model'

/**
 * Estado completo del formulario de filtros.
 *
 * Type y Trigger reutilizan las mismas claves categóricas que `CardEntry`.
 * TypeScript puede avisar así si la interfaz intenta enviar un valor que el
 * mapper o una futura fuente de datos no reconoce.
 */
export type CardFilters = {
  search: string
  grade: string
  nation: string
  clan: string
  type: CardKind | 'all'
  trigger: TriggerKind | 'all'
  generation: string
  boosterSet: string
}

export type CardSearchScope =
  | 'none'
  | 'set'
  | 'generation'

export const createDefaultCardFilters = (): CardFilters => ({
  search: '',
  grade: 'all',
  nation: 'all',
  clan: 'all',
  type: 'all',
  trigger: 'all',
  generation: 'all',
  boosterSet: 'all',
})
