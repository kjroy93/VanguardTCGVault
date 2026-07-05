<script setup lang="ts">
import type { CardEntry } from '@/models/card-entry.model'

defineProps<{
  card: CardEntry
}>()
</script>

<template>
  <article
    class="flex gap-4 p-4 rounded-lg border border-border bg-card"
  >
    <div
      class="w-24 shrink-0 aspect-[5/7] rounded-md overflow-hidden border border-border bg-muted"
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
        class="w-full h-full flex items-center justify-center p-2 text-center text-xs text-muted-foreground"
      >
        Imagen pendiente
      </div>
    </div>

    <div class="min-w-0 flex-1">
      <p class="text-xs text-muted-foreground">
        {{ card.cardNumber }}
      </p>

      <h2 class="mt-1 font-medium">
        {{ card.name }}
      </h2>

      <p
        v-if="card.nation || card.grade || card.rarity"
        class="mt-2 text-sm text-muted-foreground"
      >
        <span v-if="card.nation">
          {{ card.nation }}
        </span>

        <span v-if="card.grade">
          · Grade {{ card.grade }}
        </span>

        <span v-if="card.rarity">
          · {{ card.rarity }}
        </span>
      </p>
    </div>
  </article>
</template>