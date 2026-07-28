<script setup lang="ts">
import { computed, watch } from 'vue'

import type { CardEntry } from '@/models/card-entry.model'
import type { CardDetail } from '@/models/card-detail.model'

import CardItem from './CardItem.vue'
import CardRow from './CardRow.vue'

type PaginationItem =
  | number
  | 'ellipsis-left'
  | 'ellipsis-right'

const props = defineProps<{
  cards: CardEntry[]
  page: number
  viewMode: 'grid' | 'list'

  cardDetails: Record<string, CardDetail>
  loadingDetailCardIds: Record<string, boolean>
  failedDetailCardIds: Record<string, boolean>

  searchText: string
}>()

const emit = defineEmits<{
  (event: 'update:page', value: number): void
}>()

const perPage = 24

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.cards.length / perPage))
)

const paginatedCards = computed(() => {
  // Esta colección es la que consumen los `v-for` de la plantilla.
  const start = (props.page - 1) * perPage

  return props.cards.slice(start, start + perPage)
})

const paginationItems = computed<PaginationItem[]>(() => {
  const total = totalPages.value
  const current = props.page

  if (total <= 5) {
    return Array.from(
      { length: total },
      (_, index) => index + 1
    )
  }

  if (current <= 3) {
    return [
      1,
      2,
      3,
      'ellipsis-right',
      total,
    ]
  }

  if (current >= total - 2) {
    return [
      1,
      'ellipsis-left',
      total - 2,
      total - 1,
      total,
    ]
  }

  return [
    1,
    'ellipsis-left',
    current - 1,
    current,
    current + 1,
    'ellipsis-right',
    total,
  ]
})

const goToPage = (targetPage: number) => {
  if (
    targetPage < 1 ||
    targetPage > totalPages.value ||
    targetPage === props.page
  ) {
    return
  }

  emit('update:page', targetPage)
}

const preloadedImageUrls = new Set<string>()

const preloadImages = (cards: CardEntry[]) => {
  for (const card of cards) {
    if (!card.imageUrl) {
      continue
    }

    if (preloadedImageUrls.has(card.imageUrl)) {
      continue
    }

    const image = new Image()
    image.src = card.imageUrl

    preloadedImageUrls.add(card.imageUrl)
  }
}

const preloadNextPage = () => {
  const nextPageStart = props.page * perPage

  preloadImages(
    props.cards.slice(
      nextPageStart,
      nextPageStart + perPage
    )
  )
}

watch(
  () => ({
    page: props.page,
    imageSignature: props.cards
      .map(card => card.imageUrl ?? '')
      .join('|'),
  }),
  () => {
    preloadNextPage()
  },
  { immediate: true }
)
</script>

<template>
  <div class="space-y-6">
    <p
      v-if="cards.length === 0"
      class="py-12 text-center text-muted-foreground"
    >
      No hay cartas que coincidan con los filtros actuales.
    </p>

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

    <div
      v-else
      class="space-y-3"
    >
      <CardRow
        v-for="card in paginatedCards"
        :key="card.id"
        :card="card"
        :detail="cardDetails[card.id]"
        :detail-loading="Boolean(loadingDetailCardIds[card.id])"
        :detail-failed="Boolean(failedDetailCardIds[card.id])"
        :search-text="searchText"
      />
    </div>

    <nav
      v-if="cards.length > perPage"
      class="flex flex-wrap items-center justify-center gap-1"
      aria-label="Paginación de cartas"
    >
      <button
        type="button"
        class="h-9 px-3 rounded-md text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted"
        :disabled="page === 1"
        @click="goToPage(page - 1)"
      >
        ‹ Previous
      </button>

      <template
        v-for="item in paginationItems"
        :key="String(item)"
      >
        <span
          v-if="item === 'ellipsis-left' || item === 'ellipsis-right'"
          class="w-9 text-center text-sm text-muted-foreground"
        >
          …
        </span>

        <button
          v-else
          type="button"
          class="w-9 h-9 rounded-md text-sm font-medium transition-colors hover:bg-muted"
          :class="{
            'bg-primary text-primary-foreground hover:bg-primary':
              item === page,
          }"
          :aria-current="item === page ? 'page' : undefined"
          @click="goToPage(item)"
        >
          {{ item }}
        </button>
      </template>

      <button
        type="button"
        class="h-9 px-3 rounded-md text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted"
        :disabled="page === totalPages"
        @click="goToPage(page + 1)"
      >
        Next ›
      </button>
    </nav>
  </div>
</template>
