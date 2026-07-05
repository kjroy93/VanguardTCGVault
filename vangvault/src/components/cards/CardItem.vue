<script setup lang="ts">
import type { CardEntry } from '@/models/card-entry.model'

defineProps<{
  card: CardEntry
}>()
</script>

<template>
  <article class="group min-w-0">
    <div
      class="aspect-[5/7] rounded-md overflow-hidden border border-border bg-muted"
    >
      <img
        v-if="card.imageUrl"
        :src="card.imageUrl"
        :alt="card.name"
        class="w-full h-full object-cover"
        loading="lazy"
      />

      <div
        v-else
        class="w-full h-full flex items-center justify-center p-4 text-center text-xs text-muted-foreground"
      >
        Imagen pendiente
      </div>
    </div>

    <p class="mt-2 text-xs text-muted-foreground">
      {{ card.cardNumber }}
    </p>

    <p
      class="text-sm truncate"
      :title="card.name"
    >
      {{ card.name }}
    </p>
  </article>
</template>