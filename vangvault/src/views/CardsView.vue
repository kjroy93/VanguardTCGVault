<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import { storeToRefs } from 'pinia'
import { LayoutGrid, List } from 'lucide-vue-next'

import type { CardEntry } from '@/models/card-entry.model'

import CardGrid from '@/components/cards/CardGrid.vue'
import CardFiltersPanel from '@/components/filters/CardFilters.vue'

import {
  createDefaultCardFilters,
  type CardFilters,
} from '@/components/filters/card-filters.types'

import {
  ToggleGroup,
  ToggleGroupItem,
} from '@/components/ui/toggle-group'

import { useBoosterStore } from '@/stores/booster/booster.store'
import { useCardStore } from '@/stores/card/card.store'

import {
  searchCardsByWikiMetadata,
  searchCardsByWikiText,
} from '@/stores/card/helpers/card-text-search.api'

const PAGE_SIZE = 20

const boosterStore = useBoosterStore()
const cardStore = useCardStore()

const {
  sets: boosterSets,
  loading: boosterSetsLoading,
} = storeToRefs(boosterStore)

const {
  selectedCards,
  selectedSetUrl,
  selectedGeneration,
  loadingSetUrl,
  generationStatus,
  generationProgress,
  errorMessage,
  cardDetailsById,
  loadingDetailCardIds,
  failedDetailCardIds,
} = storeToRefs(cardStore)

const draftFilters = ref<CardFilters>(
  createDefaultCardFilters()
)

/**
 * Solo Set, Gen y texto pasan a este estado
 * cuando el usuario pulsa Buscar.
 */
const appliedFilters = ref<CardFilters>(
  createDefaultCardFilters()
)

const page = ref(1)
const viewMode = ref<'grid' | 'list'>('grid')

const textSearchLoading = ref(false)
const textSearchError = ref<string | null>(null)
const textSearchWasTruncated = ref(false)

const textMatchedCardIds = ref<Set<string> | null>(
  null
)

const advancedFiltersLoading = ref(false)
const advancedFiltersError = ref<string | null>(null)
const advancedFiltersWasTruncated = ref(false)

const advancedMatchedCardIds = ref<Set<string> | null>(
  null
)

let advancedSearchVersion = 0

const canSearch = computed(() =>
  draftFilters.value.boosterSet !== 'all' ||
  draftFilters.value.generation !== 'all'
)

const searchDisabledReason = computed(() => {
  if (boosterSetsLoading.value) {
    return 'Cargando la lista de booster sets...'
  }

  return 'Selecciona un booster set o una generación antes de buscar.'
})

const hasAppliedTextSearch = computed(() =>
  appliedFilters.value.search.trim().length > 0
)

const hasActiveAdvancedFilters = computed(() =>
  draftFilters.value.clan !== 'all' ||
  draftFilters.value.type !== 'all' ||
  draftFilters.value.trigger !== 'all'
)

const advancedFilterKey = computed(() =>
  [
    draftFilters.value.clan,
    draftFilters.value.type,
    draftFilters.value.trigger,
  ].join('|')
)

const isLoadingSelectedSet = computed(() =>
  selectedSetUrl.value !== null &&
  selectedSetUrl.value === loadingSetUrl.value
)

const isLoadingSelectedGeneration = computed(() => {
  const generation = selectedGeneration.value

  if (!generation) {
    return false
  }

  return generationStatus.value[generation] === 'loading'
})

const isSearching = computed(() =>
  isLoadingSelectedSet.value ||
  isLoadingSelectedGeneration.value ||
  textSearchLoading.value
)

const currentGenerationProgress = computed(() => {
  const generation = selectedGeneration.value

  if (!generation) {
    return null
  }

  return generationProgress.value[generation] ?? null
})

const hasLoadedScope = computed(() =>
  selectedSetUrl.value !== null ||
  selectedGeneration.value !== null
)

/**
 * Ámbito cargado por Buscar:
 * Set / Gen / texto.
 */
const scopedCards = computed(() =>
  selectedCards.value.filter(card => {
    const matchesText =
      !hasAppliedTextSearch.value ||
      textMatchedCardIds.value?.has(card.id) === true

    const matchesSet =
      appliedFilters.value.boosterSet === 'all' ||
      card.setKey === appliedFilters.value.boosterSet

    const matchesGeneration =
      appliedFilters.value.generation === 'all' ||
      card.generation === appliedFilters.value.generation

    return (
      matchesText &&
      matchesSet &&
      matchesGeneration
    )
  })
)

/**
 * Filtros locales puros: no hacen fetch.
 */
const basicFilteredCards = computed(() =>
  scopedCards.value.filter(card => {
    const matchesGrade =
      draftFilters.value.grade === 'all' ||
      card.grade === draftFilters.value.grade

    const matchesNation =
      draftFilters.value.nation === 'all' ||
      card.nationKey === draftFilters.value.nation

    return matchesGrade && matchesNation
  })
)

const advancedScopeKey = computed(() =>
  basicFilteredCards.value
    .map(card => card.id)
    .join('|')
)

/**
 * Mientras se consulta Type / Trigger / Clan,
 * mantenemos los resultados básicos visibles.
 * Al volver la respuesta se refinan automáticamente.
 */
const filteredCards = computed(() => {
  if (
    !hasActiveAdvancedFilters.value ||
    !advancedMatchedCardIds.value
  ) {
    return basicFilteredCards.value
  }

  return basicFilteredCards.value.filter(card =>
    advancedMatchedCardIds.value?.has(card.id)
  )
})

const visibleCards = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE

  return filteredCards.value.slice(
    start,
    start + PAGE_SIZE
  )
})

const loadingMessage = computed(() => {
  if (textSearchLoading.value) {
    return `Buscando "${appliedFilters.value.search}" dentro de los textos de carta...`
  }

  if (isLoadingSelectedSet.value) {
    return 'Cargando Card List del booster...'
  }

  if (isLoadingSelectedGeneration.value) {
    const generation = selectedGeneration.value
    const progress = currentGenerationProgress.value

    if (!progress) {
      return `Preparando generación ${generation}...`
    }

    const failureText =
      progress.failed > 0
        ? ` · ${progress.failed} sets con error`
        : ''

    return `Preparando generación ${generation}: ${progress.completed} / ${progress.total} sets${failureText}`
  }

  return ''
})

const advancedFilterStatus = computed(() => {
  if (!hasActiveAdvancedFilters.value) {
    return null
  }

  if (advancedFiltersLoading.value) {
    return 'Aplicando filtros avanzados en la wiki...'
  }

  if (advancedFiltersError.value) {
    return advancedFiltersError.value
  }

  return null
})

const handleSearch = async (
  requestedFilters: CardFilters
) => {
  advancedSearchVersion += 1
  advancedMatchedCardIds.value = null
  advancedFiltersError.value = null
  advancedFiltersWasTruncated.value = false

  appliedFilters.value = {
    ...requestedFilters,
  }

  page.value = 1

  textSearchError.value = null
  textSearchWasTruncated.value = false
  textMatchedCardIds.value = null

  try {
    let scopeCards: CardEntry[] = []

    if (requestedFilters.boosterSet !== 'all') {
      const booster = boosterSets.value.find(
        item => item.url === requestedFilters.boosterSet
      )

      if (!booster) {
        throw new Error(
          'No se encontró el booster seleccionado.'
        )
      }

      scopeCards = await cardStore.loadCardsFromBooster(
        booster
      )
    } else if (requestedFilters.generation !== 'all') {
      scopeCards =
        await cardStore.loadCardsFromGeneration(
          requestedFilters.generation,
          boosterSets.value
        )
    }

    if (!requestedFilters.search.trim()) {
      return
    }

    textSearchLoading.value = true

    const searchResult = await searchCardsByWikiText(
      scopeCards,
      requestedFilters.search
    )

    textMatchedCardIds.value = searchResult.cardIds
    textSearchWasTruncated.value =
      searchResult.wasTruncated
  } catch (error) {
    textSearchError.value =
      error instanceof Error
        ? error.message
        : 'No se pudo buscar en los textos de carta.'

    console.error(
      'No se pudo completar la búsqueda',
      error
    )
  } finally {
    textSearchLoading.value = false
  }
}

const applyAdvancedFilters = async (): Promise<void> => {
  const currentVersion = ++advancedSearchVersion

  advancedMatchedCardIds.value = null
  advancedFiltersError.value = null
  advancedFiltersWasTruncated.value = false

  if (
    !hasLoadedScope.value ||
    !hasActiveAdvancedFilters.value
  ) {
    advancedFiltersLoading.value = false
    return
  }

  const cards = [...basicFilteredCards.value]

  if (cards.length === 0) {
    advancedMatchedCardIds.value = new Set()
    advancedFiltersLoading.value = false
    return
  }

  advancedFiltersLoading.value = true

  try {
    const result =
      await searchCardsByWikiMetadata(cards, {
        clan: draftFilters.value.clan,
        type: draftFilters.value.type,
        trigger: draftFilters.value.trigger,
      })

    if (currentVersion !== advancedSearchVersion) {
      return
    }

    advancedMatchedCardIds.value = result.cardIds
    advancedFiltersWasTruncated.value =
      result.wasTruncated
  } catch (error) {
    if (currentVersion !== advancedSearchVersion) {
      return
    }

    advancedFiltersError.value =
      error instanceof Error
        ? error.message
        : 'No se pudieron aplicar los filtros avanzados.'
  } finally {
    if (currentVersion === advancedSearchVersion) {
      advancedFiltersLoading.value = false
    }
  }
}

/**
 * Type / Trigger / Clan son reactivos,
 * pero no descargan detalles de todas las cartas.
 */
watch(
  [
    hasLoadedScope,
    hasActiveAdvancedFilters,
    advancedFilterKey,
    advancedScopeKey,
  ],
  () => {
    void applyAdvancedFilters()
  },
  {
    immediate: true,
  }
)

/**
 * Detalles e imágenes para la página visible.
 * Esto permite la vista fila con efecto sin indexar
 * todas las cartas de una generación.
 */
watch(
  [visibleCards, viewMode],
  ([cards, mode]) => {
    if (cards.length === 0) {
      return
    }

    void cardStore.loadImagesForCards(cards)

    if (mode === 'list') {
      void cardStore.loadDetailsForCards(cards)
    }
  },
  {
    immediate: true,
  }
)

watch(
  filteredCards,
  cards => {
    const maxPage = Math.max(
      1,
      Math.ceil(cards.length / PAGE_SIZE)
    )

    if (page.value > maxPage) {
      page.value = maxPage
    }
  }
)

watch(
  () => [
    draftFilters.value.nation,
    draftFilters.value.grade,
    draftFilters.value.clan,
    draftFilters.value.type,
    draftFilters.value.trigger,
  ],
  () => {
    page.value = 1
  }
)

onMounted(async () => {
  if (
    boosterSets.value.length === 0 &&
    !boosterSetsLoading.value
  ) {
    try {
      await boosterStore.loadFromApi()
    } catch (error) {
      console.error(
        'No se pudieron cargar los booster sets',
        error
      )
    }
  }
})
</script>

<template>
  <div class="w-full border-b border-border bg-card">
    <div
      class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between"
    >
      <span class="text-lg font-semibold">
        Cards
      </span>

      <div class="flex items-center gap-4">
        <span class="text-sm text-muted-foreground">
          {{ filteredCards.length }} cartas
        </span>

        <ToggleGroup
          v-model="viewMode"
          type="single"
          variant="outline"
          size="sm"
        >
          <ToggleGroupItem value="grid">
            <LayoutGrid class="w-4 h-4" />
          </ToggleGroupItem>

          <ToggleGroupItem value="list">
            <List class="w-4 h-4" />
          </ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>
  </div>

  <main class="max-w-7xl mx-auto px-4 py-6 space-y-6">
    <CardFiltersPanel
      v-model:filters="draftFilters"
      :booster-sets="boosterSets"
      :booster-sets-loading="boosterSetsLoading"
      :can-search="canSearch"
      :search-disabled-reason="searchDisabledReason"
      :searching="isSearching"
      @search="handleSearch"
    />

    <p
      v-if="isSearching"
      class="py-14 text-center text-muted-foreground"
    >
      {{ loadingMessage }}
    </p>

    <p
      v-else-if="textSearchError || errorMessage"
      class="py-14 text-center text-destructive"
    >
      {{ textSearchError ?? errorMessage }}
    </p>

    <p
      v-else-if="!hasLoadedScope"
      class="py-14 text-center text-muted-foreground"
    >
      Selecciona un booster set o una generación y pulsa Buscar.
    </p>

    <template v-else>
      <p
        v-if="textSearchWasTruncated"
        class="text-sm text-amber-500"
      >
        La búsqueda textual devolvió demasiados resultados. Añade más términos o filtros.
      </p>

      <p
        v-if="advancedFiltersWasTruncated"
        class="text-sm text-amber-500"
      >
        La wiki devolvió demasiados resultados para este filtro avanzado. El resultado puede requerir acotarlo por generación o set.
      </p>

      <p
        v-if="advancedFilterStatus"
        class="text-sm"
        :class="advancedFiltersError
          ? 'text-destructive'
          : 'text-muted-foreground'"
      >
        {{ advancedFilterStatus }}
      </p>

      <CardGrid
        :cards="filteredCards"
        :page="page"
        :view-mode="viewMode"
        :card-details="cardDetailsById"
        :loading-detail-card-ids="loadingDetailCardIds"
        :failed-detail-card-ids="failedDetailCardIds"
        :search-text="appliedFilters.search"
        @update:page="page = $event"
      />
    </template>
  </main>
</template>