export type CardFilterType =
  | 'unit'
  | 'trigger'
  | 'order'
  | 'blitz'

export type CardTrigger =
  | 'draw'
  | 'critical'
  | 'front'
  | 'heal'
  | 'over'

export type CardDetail = {
  cardId: string

  effectEn?: string
  effectJp?: string

  clan?: string

  /**
   * Valores internos usados por el filtro visual:
   * unit | trigger | order | blitz
   */
  cardType?: CardFilterType

  /**
   * draw | critical | front | heal | over
   */
  trigger?: CardTrigger
}