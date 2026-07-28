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

/**
 * Estados posibles al cargar una generación completa.
 *
 * Se guardan por generación para evitar repetir una carga ya terminada y para
 * que la interfaz pueda mostrar progreso o error.
 */
type GenerationLoadStatus =
  | 'idle'
  | 'loading'
  | 'ready'
  | 'error'

/** Contadores que se muestran mientras se descargan varios sets. */
type GenerationProgress = {
  completed: number
  total: number
  failed: number
}

/**
 * Forma completa del estado de cartas.
 *
 * Los objetos `Record` funcionan como diccionarios: permiten encontrar datos
 * rápidamente usando la URL del set, la generación o el id de una carta.
 */
type CardStoreState = {
  /** Card Lists ya normalizadas y guardadas en caché. */
  cardsBySet: Record<string, CardEntry[]>
  cardsByGeneration: Record<string, CardEntry[]>

  /** Datos detallados e indicadores de carga de cada carta. */
  cardDetailsById: Record<string, CardDetail>
  loadingDetailCardIds: Record<string, boolean>
  failedDetailCardIds: Record<string, boolean>

  /** Ámbito elegido mediante el botón Buscar. */
  selectedSetUrl: string | null
  selectedGeneration: string | null

  /** Indicadores para no lanzar la misma petición de imagen dos veces. */
  loadingSetUrl: string | null
  loadingImageSetUrl: string | null
  loadingImageCardIds: Record<string, boolean>

  /** Estado y progreso cuando se carga una generación entera. */
  generationStatus: Record<string, GenerationLoadStatus>
  generationProgress: Record<string, GenerationProgress>

  /** Mensajes que puede enseñar la vista si algo falla. */
  errorMessage: string | null
  imageErrorMessage: string | null
}

/**
 * Crea los contadores iniciales de una carga por generación.
 */
const createDefaultGenerationProgress = (
  total = 0
): GenerationProgress => ({
  completed: 0,
  total,
  failed: 0,
})

export const useCardStore = defineStore('card', {
  /**
   * ESTADO INICIAL
   *
   * Empieza sin cartas ni selección. Los datos se incorporan bajo demanda
   * cuando el usuario pulsa Buscar.
   */
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
    /**
     * Devuelve las cartas correspondientes a la selección actual.
     *
     * La vista no necesita saber en qué caché están guardadas: recibe la lista
     * del set, la lista de la generación o un array vacío.
     */
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
    /**
     * Flujo de un set:
     * URL del booster -> HTML -> filas de la Card List -> `CardEntry[]`.
     * El resultado queda en caché dentro de `cardsBySet`.
     */
    async ensureCardsForBooster(
      booster: BoosterSet
    ): Promise<CardEntry[]> {
      const setUrl = booster.url
      const cachedCards = this.cardsBySet[setUrl]

      /** Si el set ya se descargó, se reutiliza y no se vuelve a hacer fetch. */
      if (cachedCards) {
        return cachedCards
      }

      const html = await fetchBoosterSetCardListHtml(booster)
      const scrapedRows = extractCardListRowsFromHtml(html)
      const cards = mapCardListRowsToEntries(
        scrapedRows,
        booster
      )

      this.cardsBySet[setUrl] = cards

      return cards
    },

    /**
     * Selecciona un set, carga sus cartas y pone en marcha sus imágenes.
     *
     * Las cartas se esperan porque son necesarias para renderizar. Las imágenes
     * se lanzan en segundo plano para que la lista aparezca antes.
     */
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

        /**
         * Pinia provoca el rerender cuando llegue cada `imageUrl`, por eso no
         * bloqueamos aquí el resultado principal con `await`.
         */
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

    /**
     * Carga todos los sets pertenecientes a una generación.
     *
     * Limita la concurrencia a tres sets, actualiza el progreso y permite que
     * un set falle sin cancelar automáticamente los demás.
     */
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

      const currentStatus = this.generationStatus[generation] ?? 'idle'

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
        /**
         * `runWithConcurrency` reparte los sets entre tres trabajadores.
         * Cada trabajador devuelve las cartas o un array vacío si ese set falla.
         */
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

        /**
         * Una misma carta puede reaparecer en varios productos. El `Map` usa su
         * id como clave y deja una sola copia en el resultado de generación.
         */
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

    /**
     * Carga imágenes únicamente para el grupo de cartas que recibe.
     *
     * `CardsView.vue` la usa con la página visible para no pedir cientos de
     * imágenes que todavía están fuera de pantalla.
     */
    async loadImagesForCards(cards: CardEntry[]): Promise<void> {
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

        /**
         * Devuelve nuevas cartas con la imagen encontrada. Se crean objetos
         * nuevos para que Vue detecte con claridad el cambio reactivo.
         */
        const applyImages = (collection: CardEntry[]): CardEntry[] =>
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

    /**
     * Descarga efecto, clan, tipo y trigger para varias cartas.
     *
     * Solo se usa cuando esos datos hacen falta. Recuerda qué cartas fallaron
     * para no repetir indefinidamente la misma petición.
     */
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

      /** Resultado interno de cada trabajador de detalles. */
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

    /**
     * Carga todas las imágenes pendientes de un booster concreto.
     *
     * Actualiza tanto la caché por set como la caché por generación para que
     * ambas vistas compartan las mismas URLs de imagen.
     */
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

    /** Deja de mostrar un set concreto y limpia su mensaje de error. */
    clearSelectedBooster(): void {
      this.selectedSetUrl = null
      this.errorMessage = null
    },

    /** Deja de mostrar una generación y limpia su mensaje de error. */
    clearSelectedGeneration(): void {
      this.selectedGeneration = null
      this.errorMessage = null
    },

    /** Borra cualquier ámbito de búsqueda seleccionado. */
    clearSelection(): void {
      this.selectedSetUrl = null
      this.selectedGeneration = null
      this.errorMessage = null
    },
  },
})
