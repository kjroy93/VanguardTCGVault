import { defineStore } from 'pinia'

export const useFilterStore = defineStore('filter', {
  state: () => ({
    booster: null,
    nation: null,
    power: null,
    shield: null
  }),

  actions: {
    setFilter(key, value) {
      this[key] = value
    },

    resetFilters() {
      this.booster = null
      this.nation = null
      this.power = null
      this.shield = null
    }
  }
})