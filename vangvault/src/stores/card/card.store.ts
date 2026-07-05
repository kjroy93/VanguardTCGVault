import { defineStore } from 'pinia'

import type { BoosterSet } from '@/models/booster.model'
import type { CardEntry } from '@/models/card-entry.model'
import type { CardDetail } from '@/models/card-detail.model'

import { fetchBoosterSetCardListHtml } from './helpers/card-list.api'
import { extractCardListRowsFromHtml } from './helpers/card-list.extractor'
import { mapCardListRowsToEntries } from './helpers/card-list.mapper'
import { fetchCardImageUrls } from './helpers/card-image.api'
import { fetchCardDetail } from './helpers/card-detail.api'
import { runWithConcurrency } from './helpers/card-load.utils'

type GenerationLoadStatus =
  | 'idle'
  | 'loading'
  | 'ready'
  | 'error'

type GenerationProgress = {
  completed: number
  total: number
  failed: number
}

type CardStoreState = {
  cardsBySet: Record<string, CardEntry[]>
  cardsByGeneration: Record<string, CardEntry[]>

  cardDetailsById: Record<string, CardDetail>
  loadingDetailCardIds: Record<string, boolean>
  failedDetailCardIds: Record<string, boolean>

  selectedSetUrl: string | null
  selectedGeneration: string | null

  loadingSetUrl: string | null
  loadingImageSetUrl: string | null
  loadingImageCardIds: Record<string, boolean>

  generationStatus: Record<string, GenerationLoadStatus>
  generationProgress: Record<string, GenerationProgress>

  errorMessage: string | null
  imageErrorMessage: string | null
}

const createDefaultGenerationProgress = (
  total = 0
): GenerationProgress => ({
  completed: 0,
  total,
  failed: 0,
})

export const useCardStore = defineStore('card', {
  state: (): CardStoreState => ({
    cardsBySet: {},
    cardsByGeneration: {},

    cardDetailsById: {},
    loadingDetailCardIds: {},
    failedDetailCardIds: {},

    selectedSetUrl: null,
    selectedGeneration: null,

    loadingSetUrl: null,
    loadingImageSetUrl: null,
    loadingImageCardIds: {},

    generationStatus: {},
    generationProgress: {},

    errorMessage: null,
    imageErrorMessage: null,
  }),

  getters: {
    selectedCards(state): CardEntry[] {
      if (state.selectedSetUrl) {
        return state.cardsBySet[state.selectedSetUrl] ?? []
      }

      if (state.selectedGeneration) {
        return (
          state.cardsByGeneration[
            state.selectedGeneration
          ] ?? []
        )
      }

      return []
    },
  },

  actions: {
    async ensureCardsForBooster(
      booster: BoosterSet
    ): Promise<CardEntry[]> {
      const setUrl = booster.url
      const cachedCards = this.cardsBySet[setUrl]

      if (cachedCards) {
        return cachedCards
      }

      const html = await fetchBoosterSetCardListHtml(
        booster
      )

      const scrapedRows = extractCardListRowsFromHtml(
        html
      )

      const cards = mapCardListRowsToEntries(
        scrapedRows,
        booster
      )

      this.cardsBySet[setUrl] = cards

      return cards
    },

    async loadCardsFromBooster(
      booster: BoosterSet
    ): Promise<CardEntry[]> {
      const setUrl = booster.url

      this.selectedSetUrl = setUrl
      this.selectedGeneration = null
      this.errorMessage = null
      this.loadingSetUrl = setUrl

      try {
        const cards = await this.ensureCardsForBooster(
          booster
        )

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

    async loadCardsFromGeneration(
      generation: string,
      boosters: BoosterSet[]
    ): Promise<CardEntry[]> {
      const generationBoosters = boosters.filter(
        booster => booster.generation === generation
      )

      if (generationBoosters.length === 0) {
        throw new Error(
          `No se encontraron boosters para la generación ${generation}`
        )
      }

      this.selectedSetUrl = null
      this.selectedGeneration = generation
      this.errorMessage = null

      const currentStatus =
        this.generationStatus[generation] ?? 'idle'

      if (currentStatus === 'ready') {
        return this.cardsByGeneration[generation] ?? []
      }

      if (currentStatus === 'loading') {
        return this.cardsByGeneration[generation] ?? []
      }

      this.generationStatus[generation] = 'loading'

      this.generationProgress[generation] =
        createDefaultGenerationProgress(
          generationBoosters.length
        )

      try {
        const cardsByBooster = await runWithConcurrency(
          generationBoosters,
          3,
          async booster => {
            try {
              return await this.ensureCardsForBooster(
                booster
              )
            } catch (error) {
              const progress =
                this.generationProgress[generation]

              if (progress) {
                progress.failed += 1
              }

              console.warn(
                `No se pudo cargar el set ${booster.code ?? booster.name}`,
                error
              )

              return []
            } finally {
              const progress =
                this.generationProgress[generation]

              if (progress) {
                progress.completed += 1
              }
            }
          }
        )

        const uniqueCards = new Map<string, CardEntry>()

        for (const cards of cardsByBooster) {
          for (const card of cards) {
            uniqueCards.set(card.id, card)
          }
        }

        const generationCards = [
          ...uniqueCards.values(),
        ]

        if (generationCards.length === 0) {
          throw new Error(
            `No se pudo cargar ninguna carta de la generación ${generation}`
          )
        }

        this.cardsByGeneration[generation] =
          generationCards

        this.generationStatus[generation] = 'ready'

        return generationCards
      } catch (error) {
        this.generationStatus[generation] = 'error'

        this.errorMessage =
          error instanceof Error
            ? error.message
            : 'No se pudo cargar la generación'

        throw error
      }
    },

    async loadImagesForCards(
      cards: CardEntry[]
    ): Promise<void> {
      const cardsToLoad = cards.filter(card => {
        return (
          !card.imageUrl &&
          !this.loadingImageCardIds[card.id]
        )
      })

      if (cardsToLoad.length === 0) {
        return
      }

      for (const card of cardsToLoad) {
        this.loadingImageCardIds[card.id] = true
      }

      try {
        const imageUrls = await fetchCardImageUrls(
          cardsToLoad
        )

        const applyImages = (
          collection: CardEntry[]
        ): CardEntry[] =>
          collection.map(card => ({
            ...card,
            imageUrl:
              imageUrls[card.id] ?? card.imageUrl,
          }))

        for (const setUrl of Object.keys(
          this.cardsBySet
        )) {
          this.cardsBySet[setUrl] = applyImages(
            this.cardsBySet[setUrl]
          )
        }

        for (const generation of Object.keys(
          this.cardsByGeneration
        )) {
          this.cardsByGeneration[generation] =
            applyImages(
              this.cardsByGeneration[generation]
            )
        }
      } catch (error) {
        this.imageErrorMessage =
          error instanceof Error
            ? error.message
            : 'No se pudieron cargar algunas miniaturas'

        console.warn(
          'No se pudieron cargar las imágenes visibles',
          error
        )
      } finally {
        for (const card of cardsToLoad) {
          delete this.loadingImageCardIds[card.id]
        }
      }
    },

    async loadDetailsForCards(
      cards: CardEntry[]
    ): Promise<void> {
      const cardsToLoad = cards.filter(card => {
        return (
          !this.cardDetailsById[card.id] &&
          !this.loadingDetailCardIds[card.id] &&
          !this.failedDetailCardIds[card.id]
        )
      })

      if (cardsToLoad.length === 0) {
        return
      }

      for (const card of cardsToLoad) {
        this.loadingDetailCardIds[card.id] = true
      }

      type DetailLoadResult = {
        cardId: string
        detail?: CardDetail
        failed: boolean
      }

      try {
        const results = await runWithConcurrency<
          CardEntry,
          DetailLoadResult
        >(
          cardsToLoad,
          4,
          async card => {
            try {
              return {
                cardId: card.id,
                detail: await fetchCardDetail(card),
                failed: false,
              }
            } catch (error) {
              console.warn(
                `No se pudo cargar el efecto de ${card.cardNumber}`,
                error
              )

              return {
                cardId: card.id,
                failed: true,
              }
            }
          }
        )

        for (const result of results) {
          if (result.detail) {
            this.cardDetailsById[result.cardId] =
              result.detail

            delete this.failedDetailCardIds[
              result.cardId
            ]

            continue
          }

          if (result.failed) {
            this.failedDetailCardIds[result.cardId] =
              true
          }
        }
      } finally {
        for (const card of cardsToLoad) {
          delete this.loadingDetailCardIds[card.id]
        }
      }
    },

    async loadImagesForBooster(
      booster: BoosterSet
    ): Promise<void> {
      const setUrl = booster.url
      const currentCards =
        this.cardsBySet[setUrl] ?? []

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
          imageUrl:
            imageUrls[card.id] ?? card.imageUrl,
        }))

        this.cardsBySet[setUrl] = updatedCards

        const generation = booster.generation

        if (generation) {
          const generationCards =
            this.cardsByGeneration[generation]

          if (generationCards) {
            this.cardsByGeneration[generation] =
              generationCards.map(card => ({
                ...card,
                imageUrl:
                  imageUrls[card.id] ??
                  card.imageUrl,
              }))
          }
        }
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

    clearSelectedGeneration(): void {
      this.selectedGeneration = null
      this.errorMessage = null
    },

    clearSelection(): void {
      this.selectedSetUrl = null
      this.selectedGeneration = null
      this.errorMessage = null
    },
  },
})