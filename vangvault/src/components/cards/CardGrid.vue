<script setup lang="ts">
import { computed } from 'vue'

import type { CardEntry } from '@/models/card-entry.model'

import CardItem from './CardItem.vue'
import CardRow from './CardRow.vue'

import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'

const props = defineProps<{
  cards: CardEntry[]
  page: number
  viewMode: 'grid' | 'list'
}>()

const emit = defineEmits<{
  (event: 'update:page', value: number): void
}>()

const perPage = 20

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.cards.length / perPage))
)

const paginatedCards = computed(() => {
  const start = (props.page - 1) * perPage

  return props.cards.slice(start, start + perPage)
})
</script>

<template>
  <div class="space-y-6">
    <p
      v-if="cards.length === 0"
      class="py-12 text-center text-muted-foreground"
    >
      No hay cartas que coincidan con los filtros actuales.
    </p>

    <!-- GRID -->
    <div
      v-else-if="viewMode === 'grid'"
      class="grid grid-cols-[repeat(auto-fill,minmax(190px,1fr))] gap-3"
    >
      <CardItem
        v-for="card in paginatedCards"
        :key="card.id"
        :card="card"
      />
    </div>

    <!-- LIST -->
    <div
      v-else
      class="space-y-3"
    >
      <CardRow
        v-for="card in paginatedCards"
        :key="card.id"
        :card="card"
      />
    </div>

    <!-- PAGINATION -->
    <Pagination
      v-if="cards.length > perPage"
      :page="page"
      :items-per-page="perPage"
      :total="cards.length"
    >
      <PaginationContent v-slot="{ items }">
        <PaginationPrevious
          @click="page > 1 && emit('update:page', page - 1)"
        />

        <template
          v-for="item in items"
          :key="item.type === 'page' ? item.value : item.type"
        >
          <PaginationItem
            v-if="item.type === 'page'"
            :value="item.value"
            :is-active="item.value === page"
            @click="emit('update:page', item.value)"
          >
            {{ item.value }}
          </PaginationItem>
        </template>

        <PaginationNext
          @click="
            page < totalPages &&
            emit('update:page', page + 1)
          "
        />
      </PaginationContent>
    </Pagination>
  </div>
</template>