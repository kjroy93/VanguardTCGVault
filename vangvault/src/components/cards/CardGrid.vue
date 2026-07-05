<script setup lang="ts">
import { computed } from 'vue'
import CardItem from './CardItem.vue'
import CardRow from './CardRow.vue'

import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
  PaginationEllipsis,
} from '@/components/ui/pagination'

const props = defineProps<{
  cards: any[]
  page: number
  viewMode: 'grid' | 'list'
}>()

const emit = defineEmits<{
  (e: 'update:page', value: number): void
}>()

const perPage = 20

const totalPages = computed(() =>
  Math.ceil(props.cards.length / perPage)
)

const paginated = computed(() => {
  const start = (props.page - 1) * perPage
  return props.cards.slice(start, start + perPage)
})
</script>

<template>
  <div class="space-y-6">

    <!-- GRID -->
    <div
      v-if="viewMode === 'grid'"
      class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-3"
    >
      <CardItem
        v-for="card in paginated"
        :key="card.id"
        :card="card"
      />
    </div>

    <!-- LIST -->
    <div v-else class="space-y-4">
      <CardRow
        v-for="card in paginated"
        :key="card.id"
        :card="card"
      />
    </div>

    <!-- PAGINATION -->
    <Pagination
      :page="page"
      :items-per-page="perPage"
      :total="cards.length"
    >
      <PaginationContent v-slot="{ items }">

        <PaginationPrevious
          @click="page > 1 && emit('update:page', page - 1)"
        />

        <template v-for="(item, index) in items" :key="index">
          <PaginationItem
            v-if="item.type === 'page'"
            :value="item.value"
            :is-active="item.value === page"
            @click="emit('update:page', item.value)"
          >
            {{ item.value }}
          </PaginationItem>
        </template>

        <PaginationEllipsis />

        <PaginationNext
          @click="page < totalPages && emit('update:page', page + 1)"
        />

      </PaginationContent>
    </Pagination>

  </div>
</template>