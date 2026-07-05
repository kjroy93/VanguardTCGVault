import { defineStore } from 'pinia'

type LegacyFilterState = {
  booster: string | null
  nation: string | null
  power: number | null
  shield: number | null
}

const createDefaultState = (): LegacyFilterState => ({
  booster: null,
  nation: null,
  power: null,
  shield: null,
})

export const useFilterStore = defineStore('filter', {
  state: (): LegacyFilterState => createDefaultState(),

  actions: {
    setFilter<K extends keyof LegacyFilterState>(
      key: K,
      value: LegacyFilterState[K],
    ) {
      this.$patch({
        [key]: value,
      } as Partial<LegacyFilterState>)
    },

    resetFilters() {
      this.$patch(createDefaultState())
    },
  },
})