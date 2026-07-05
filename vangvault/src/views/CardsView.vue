<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { LayoutGrid, List } from 'lucide-vue-next'

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

const boosterStore = useBoosterStore()
const cardStore = useCardStore()

const {
  sets: boosterSets,
  loading: boosterSetsLoading,
} = storeToRefs(boosterStore)

const {
  selectedCards,
  selectedSetUrl,
  loadingSetUrl,
  errorMessage,
} = storeToRefs(cardStore)

const filters = ref<CardFilters>(
  createDefaultCardFilters()
)

const page = ref(1)
const viewMode = ref<'grid' | 'list'>('grid')

const isLoadingSelectedSet = computed(() =>
  selectedSetUrl.value !== null &&
  selectedSetUrl.value === loadingSetUrl.value
)

const searchTokens = computed(() =>
  filters.value.search
    .split(';')
    .map(token => token.trim().toLowerCase())
    .filter(Boolean)
)

const filteredCards = computed(() => {
  return selectedCards.value.filter(card => {
    const searchableText = [
      card.cardNumber,
      card.name,
      card.nation,
      card.rarity,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    const matchesSearch =
      searchTokens.value.length === 0 ||
      searchTokens.value.every(token =>
        searchableText.includes(token)
      )

    const matchesGrade =
      filters.value.grade === 'all' ||
      card.grade === filters.value.grade

    const matchesNation =
      filters.value.nation === 'all' ||
      card.nationKey === filters.value.nation

    const matchesGeneration =
      filters.value.generation === 'all' ||
      card.generation === filters.value.generation

    return (
      matchesSearch &&
      matchesGrade &&
      matchesNation &&
      matchesGeneration
    )
  })
})

watch(
  () => filters.value.boosterSet,
  async boosterUrl => {
    if (boosterUrl === 'all') {
      cardStore.clearSelectedBooster()
      return
    }

    const booster = boosterSets.value.find(
      item => item.url === boosterUrl
    )

    if (!booster) {
      return
    }

    try {
      await cardStore.loadCardsFromBooster(booster)
    } catch (error) {
      console.error(error)
    }
  }
)

watch(
  filters,
  () => {
    page.value = 1
  },
  { deep: true }
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

  <div class="max-w-7xl mx-auto px-4 py-6 space-y-6">
    <CardFiltersPanel
      v-model:filters="filters"
      :booster-sets="boosterSets"
      :booster-sets-loading="boosterSetsLoading"
    />

    <p
      v-if="filters.boosterSet === 'all'"
      class="py-14 text-center text-muted-foreground"
    >
      Selecciona un booster set para cargar sus cartas.
    </p>

    <p
      v-else-if="isLoadingSelectedSet"
      class="py-14 text-center text-muted-foreground"
    >
      Cargando Card List…
    </p>

    <p
      v-else-if="errorMessage"
      class="py-14 text-center text-destructive"
    >
      {{ errorMessage }}
    </p>

    <CardGrid
      v-else
      :cards="filteredCards"
      :page="page"
      :view-mode="viewMode"
      @update:page="page = $event"
    />
  </div>
</template>