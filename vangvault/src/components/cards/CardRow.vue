<script setup lang="ts">
import { computed } from 'vue'

import type { CardEntry } from '@/models/card-entry.model'
import type { CardDetail } from '@/models/card-detail.model'

type HighlightPart = {
  text: string
  highlighted: boolean
}

const props = withDefaults(defineProps<{
  card: CardEntry
  detail?: CardDetail
  detailLoading?: boolean
  detailFailed?: boolean
  searchText?: string
}>(), {
  detail: undefined,
  detailLoading: false,
  detailFailed: false,
  searchText: '',
})

const searchTerms = computed(() => {
  return [...new Set(
    props.searchText
      .split(';')
      .map(term => term.trim().toLowerCase())
      .filter(Boolean)
  )]
    .sort((a, b) => b.length - a.length)
})

const escapeRegExp = (value: string): string =>
  value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const getHighlightedParts = (
  value: string
): HighlightPart[] => {
  if (!value || searchTerms.value.length === 0) {
    return [{
      text: value,
      highlighted: false,
    }]
  }

  const expression = new RegExp(
    `(${searchTerms.value
      .map(escapeRegExp)
      .join('|')})`,
    'gi'
  )

  return value
    .split(expression)
    .filter(Boolean)
    .map(text => ({
      text,
      highlighted: searchTerms.value.includes(
        text.toLowerCase()
      ),
    }))
}

const effectText = computed(() =>
  props.detail?.effectEn?.trim() ?? ''
)
</script>

<template>
  <article
    class="flex items-start gap-4 p-4 rounded-lg border border-border bg-card"
  >
    <a
      :href="card.wikiUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="w-24 h-[134px] shrink-0 self-start rounded-md overflow-hidden border border-border bg-muted hover:ring-2 hover:ring-ring transition-shadow"
      :title="`Abrir ${card.name} en la wiki`"
    >
      <img
        v-if="card.imageUrl"
        :src="card.imageUrl"
        :alt="card.name"
        class="w-full h-full object-contain"
        loading="lazy"
      >

      <div
        v-else
        class="w-full h-full flex items-center justify-center p-2 text-center text-xs text-muted-foreground"
      >
        Imagen pendiente
      </div>
    </a>

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

      <section
        v-if="effectText || detailLoading || detailFailed"
        class="mt-4 border-t border-border pt-3"
      >
        <p class="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Card Effect · EN
        </p>

        <p
          v-if="detailLoading"
          class="text-sm text-muted-foreground"
        >
          Cargando efecto…
        </p>

        <p
          v-else-if="detailFailed"
          class="text-sm text-muted-foreground"
        >
          No se pudo cargar el efecto de esta carta.
        </p>

        <p
          v-else
          class="whitespace-pre-line text-sm leading-6 text-muted-foreground"
        >
          <template
            v-for="(part, index) in getHighlightedParts(effectText)"
            :key="`${index}-${part.text}`"
          >
            <mark
              v-if="part.highlighted"
              class="rounded bg-amber-300/30 px-0.5 text-amber-100"
            >
              {{ part.text }}
            </mark>

            <template v-else>
              {{ part.text }}
            </template>
          </template>
        </p>
      </section>
    </div>
  </article>
</template>