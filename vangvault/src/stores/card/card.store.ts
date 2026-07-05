import { defineStore } from 'pinia'

import type { BoosterSet } from '@/models/booster.model'
import type { CardEntry } from '@/models/card-entry.model'

import { fetchBoosterSetCardListHtml } from './helpers/card-list.api'
import { extractCardListRowsFromHtml } from './helpers/card-list.extractor'
import { mapCardListRowsToEntries } from './helpers/card-list.mapper'
import { fetchCardImageUrls } from './helpers/card-image.api'

export const useCardStore = defineStore('card', {
  state: () => ({
    cardsBySet: {} as Record<string, CardEntry[]>,

    selectedSetUrl: null as string | null,
    loadingSetUrl: null as string | null,
    loadingImageSetUrl: null as string | null,

    errorMessage: null as string | null,
    imageErrorMessage: null as string | null,
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
        void this.loadImagesForBooster(booster)
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

        // No bloquea la interfaz: primero se muestran placeholders,
        // luego se actualizan las imágenes en segundo plano.
        void this.loadImagesForBooster(booster)

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

    async loadImagesForBooster(
      booster: BoosterSet
    ): Promise<void> {
      const setUrl = booster.url
      const currentCards = this.cardsBySet[setUrl] ?? []

      const cardsWithoutImages = currentCards.filter(
        card => !card.imageUrl
      )

      if (cardsWithoutImages.length === 0) {
        return
      }

      if (this.loadingImageSetUrl === setUrl) {
        return
      }

      this.loadingImageSetUrl = setUrl
      this.imageErrorMessage = null

      try {
        const imageUrls = await fetchCardImageUrls(
          cardsWithoutImages
        )

        const updatedCards = (
          this.cardsBySet[setUrl] ?? []
        ).map(card => ({
          ...card,
          imageUrl: imageUrls[card.id] ?? card.imageUrl,
        }))

        this.cardsBySet[setUrl] = updatedCards
      } catch (error) {
        this.imageErrorMessage =
          error instanceof Error
            ? error.message
            : 'No se pudieron cargar las miniaturas'

        console.warn(
          'No se pudieron cargar las miniaturas del booster',
          error
        )
      } finally {
        if (this.loadingImageSetUrl === setUrl) {
          this.loadingImageSetUrl = null
        }
      }
    },

    clearSelectedBooster(): void {
      this.selectedSetUrl = null
      this.errorMessage = null
    },
  },
})