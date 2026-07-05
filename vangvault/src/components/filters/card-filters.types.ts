export type CardFilters = {
  search: string
  grade: string
  nation: string
  clan: string
  type: string
  trigger: string
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