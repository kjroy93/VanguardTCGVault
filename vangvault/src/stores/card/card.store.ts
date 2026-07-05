import { defineStore } from 'pinia'

import type { BoosterSet } from '@/models/booster.model'
import type { CardEntry } from '@/models/card-entry.model'

import { fetchBoosterSetCardListHtml } from './helpers/card-list.api'
import { extractCardListRowsFromHtml } from './helpers/card-list.extractor'
import { mapCardListRowsToEntries } from './helpers/card-list.mapper'

export const useCardStore = defineStore('card', {
  state: () => ({
    cardsBySet: {} as Record<string, CardEntry[]>,

    selectedSetUrl: null as string | null,
    loadingSetUrl: null as string | null,

    errorMessage: null as string | null,
  }),

  getters: {
    selectedCards(state): CardEntry[] {
      if (!state.selectedSetUrl) {
        return []
      }

      return state.cardsBySet[state.selectedSetUrl] ?? []
    },
  },

  actions: {
    async loadCardsFromBooster(
      booster: BoosterSet
    ): Promise<CardEntry[]> {
      const setUrl = booster.url

      this.selectedSetUrl = setUrl
      this.errorMessage = null

      const cachedCards = this.cardsBySet[setUrl]

      if (cachedCards) {
        return cachedCards
      }

      this.loadingSetUrl = setUrl

      try {
        const html = await fetchBoosterSetCardListHtml(booster)

        const scrapedRows = extractCardListRowsFromHtml(html)

        const cards = mapCardListRowsToEntries(
          scrapedRows,
          booster
        )

        this.cardsBySet[setUrl] = cards

        return cards
      } catch (error) {
        this.errorMessage =
          error instanceof Error
            ? error.message
            : 'No se pudieron cargar las cartas del booster'

        throw error
      } finally {
        if (this.loadingSetUrl === setUrl) {
          this.loadingSetUrl = null
        }
      }
    },

    clearSelectedBooster(): void {
      this.selectedSetUrl = null
      this.errorMessage = null
    },
  },
})