import { defineStore } from 'pinia'

export const useCardStore = defineStore('card', {
  state: () => ({
    cards: [],
    loading: false,
    page: 1,
    hasMore: true
  }),

  actions: {
    async fetchCards(filters:any) {
      this.loading = true

      // aquí luego conectarás con repository
      console.log('fetch con filtros:', filters)

      this.loading = false
    },

    reset() {
      this.cards = []
      this.page = 1
    }
  }
})