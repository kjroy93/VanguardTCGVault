<script setup lang="ts">
import { ref, computed } from 'vue'

import CardGrid from '@/components/cards/CardGrid.vue'
import CardFilters from '@/components/filters/CardFilters.vue'

import { LayoutGrid, List } from 'lucide-vue-next'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

// 🔹 TIPOS
type Filters = {
  search: string
  grade: string
  nation: string
  clan: string
  type: string
  trigger: string
  generation: string
}

type Card = {
  id: number
  name: string
  image: string
  effect?: string
  clan?: string
  grade?: string
  nation?: string
  type?: string
  trigger?: string
  generation?: string
}

// 🔹 DATA
const cards = ref<Card[]>(
  Array.from({ length: 123 }, (_, i) => ({
    id: i + 1,
    name: `Card ${i + 1}`,
    image: 'https://static.wikia.nocookie.net/cardfight/images/1/1c/Sleeve133.png/revision/latest?cb=20160712170330',
    effect: 'Sample effect text',
    clan: i % 2 === 0 ? 'Kagero' : 'Murakumo',
    grade: String(i % 5),
    nation: 'dragon_empire',
    type: 'unit',
    trigger: i % 3 === 0 ? 'critical' : '',
    generation: 'D',
  }))
)

// 🔹 STATE
const filters = ref<Filters>({
  search: '',
  grade: 'all',
  nation: 'all',
  clan: 'all',
  type: 'all',
  trigger: 'all',
  generation: 'all',
})

const page = ref(1)
const viewMode = ref<'grid' | 'list'>('grid')

// 🔹 SEARCH TOKENS (; separated)
const searchTokens = computed<string[]>(() => {
  return (filters.value.search || '')
    .split(';')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean)
})

// 🔹 FILTER LOGIC
const filteredCards = computed(() => {
  return cards.value.filter((card) => {

    // 🔎 SEARCH (AND)
    const matchesSearch =
      searchTokens.value.length === 0 ||
      searchTokens.value.every((token: string) =>
        card.name.toLowerCase().includes(token) ||
        card.effect?.toLowerCase().includes(token) ||
        card.clan?.toLowerCase().includes(token)
      )

    // 🎯 GRADE
    const matchesGrade =
      filters.value.grade === 'all' ||
      card.grade === filters.value.grade

    // 🏳️ NATION
    const matchesNation =
      filters.value.nation === 'all' ||
      card.nation === filters.value.nation

    // 🏳️ CLAN
    const matchesClan =
      filters.value.clan === 'all' ||
      card.clan === filters.value.clan

    // 🧩 TYPE
    const matchesType =
      filters.value.type === 'all' ||
      card.type === filters.value.type

    // ⚡ TRIGGER
    const matchesTrigger =
      filters.value.trigger === 'all' ||
      card.trigger === filters.value.trigger

    // 🧬 GENERATION
    const matchesGeneration =
      filters.value.generation === 'all' ||
      card.generation === filters.value.generation

    return (
      matchesSearch &&
      matchesGrade &&
      matchesNation &&
      matchesClan &&
      matchesType &&
      matchesTrigger &&
      matchesGeneration
    )
  })
})
</script>

<template>
  <!-- 🔴 HEADER FULL WIDTH -->
  <div class="w-full border-b border-border bg-card">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
      
      <!-- IZQUIERDA -->
      <div class="flex items-center gap-3">
        <span class="text-lg font-semibold">Cards</span>
      </div>

      <!-- DERECHA -->
      <div class="flex items-center gap-4">
        <span class="text-sm text-muted-foreground">
          {{ cards.length }} cartas
        </span>

        <ToggleGroup
          type="single"
          v-model="viewMode"
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

  <!-- 🟢 CONTENIDO CENTRADO -->
  <div class="max-w-7xl mx-auto px-4 py-6 space-y-6">

    <CardFilters v-model:filters="filters" />

    <CardGrid
      :cards="filteredCards"
      :page="page"
      :viewMode="viewMode"
      @update:page="page = $event"
    />

  </div>
</template>