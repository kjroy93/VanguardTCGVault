<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { BoosterSet } from '@/models/booster.model'
import type { CardFilters } from './card-filters.types'

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command'

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import {
  ToggleGroup,
  ToggleGroupItem,
} from '@/components/ui/toggle-group'

const GENERATIONS = [
  { label: 'All', value: 'all' },
  { label: 'Original', value: 'Original' },
  { label: 'G', value: 'G' },
  { label: 'V', value: 'V' },
  { label: 'D', value: 'D' },
  { label: 'DZ', value: 'DZ' },
]

const GRADES = [
  { label: 'All', value: 'all' },
  { label: '0', value: '0' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4', value: '4' },
  { label: '5+', value: '5+' },
]

const TYPES = [
  { label: 'All', value: 'all' },
  { label: 'Unit', value: 'unit' },
  { label: 'Trigger', value: 'trigger' },
  { label: 'Order', value: 'order' },
  { label: 'Blitz', value: 'blitz' },
]

const TRIGGERS = [
  { label: 'All', value: 'all' },
  { label: 'Draw', value: 'draw' },
  { label: 'Critical', value: 'critical' },
  { label: 'Front', value: 'front' },
  { label: 'Heal', value: 'heal' },
  { label: 'Over', value: 'over' },
]

const NATIONS = [
  { label: 'All', value: 'all' },
  { label: 'Dragon Empire', value: 'dragon_empire' },
  { label: 'Stoicheia', value: 'stoicheia' },
  { label: 'Dark States', value: 'dark_states' },
  { label: 'Keter Sanctuary', value: 'keter' },
  { label: 'Brandt Gate', value: 'brandt' },
  { label: 'Lyrical Monasterio', value: 'lyrical' },
]

const CLANS = [
  { name: 'Kagero', nation: 'dragon_empire' },
  { name: 'Murakumo', nation: 'dragon_empire' },
  { name: 'Nubatama', nation: 'dragon_empire' },
  { name: 'Tachikaze', nation: 'dragon_empire' },

  { name: 'Aqua Force', nation: 'stoicheia' },
  { name: 'Granblue', nation: 'stoicheia' },
  { name: 'Neo Nectar', nation: 'stoicheia' },
  { name: 'Great Nature', nation: 'stoicheia' },

  { name: 'Spike Brothers', nation: 'dark_states' },
  { name: 'Dark Irregulars', nation: 'dark_states' },
  { name: 'Pale Moon', nation: 'dark_states' },

  { name: 'Royal Paladin', nation: 'keter' },
  { name: 'Shadow Paladin', nation: 'keter' },
  { name: 'Gold Paladin', nation: 'keter' },
  { name: 'Angel Feather', nation: 'keter' },
  { name: 'Genesis', nation: 'keter' },

  { name: 'Nova Grappler', nation: 'brandt' },
  { name: 'Dimension Police', nation: 'brandt' },
  { name: 'Link Joker', nation: 'brandt' },

  { name: 'Bermuda Triangle', nation: 'lyrical' },
  { name: 'Elemental Cray', nation: null },
]

const props = withDefaults(defineProps<{
  filters: CardFilters
  boosterSets?: BoosterSet[]
  boosterSetsLoading?: boolean
  canSearch?: boolean
  searchDisabledReason?: string
  searching?: boolean
}>(), {
  boosterSets: () => [],
  boosterSetsLoading: false,
  canSearch: false,
  searchDisabledReason:
    'Selecciona un booster set o una generación.',
  searching: false,
})

const emit = defineEmits<{
  (event: 'update:filters', value: CardFilters): void
  (event: 'search', value: CardFilters): void
}>()

const local = ref<CardFilters>({
  ...props.filters,
})

const clanOpen = ref(false)
const boosterOpen = ref(false)

const availableClans = computed(() => {
  if (local.value.nation === 'all') {
    return CLANS.map(clan => clan.name)
  }

  return CLANS
    .filter(
      clan =>
        clan.nation === local.value.nation ||
        clan.nation === null
    )
    .map(clan => clan.name)
})

const boosterLabel = (booster: BoosterSet): string =>
  `[${booster.generation ?? '?'}] ${booster.code ?? '—'} — ${booster.name}`

const setCodeCollator = new Intl.Collator('en', {
  numeric: true,
  sensitivity: 'base',
})

const GENERATION_ORDER = [
  'Original',
  'G',
  'V',
  'D',
  'DZ',
]

/**
 * Orden natural de sets.
 *
 * No se ordena por el texto completo porque `VG-DZ-SS11` y
 * `VGE-DZ-SS04` quedarían separados por el prefijo regional. Se compara:
 * generación -> familia final (BT, SS...) -> número -> código completo.
 */
const compareBoosterSets = (
  a: BoosterSet,
  b: BoosterSet
): number => {
  const generationIndex = (booster: BoosterSet) => {
    const index = GENERATION_ORDER.indexOf(
      booster.generation ?? ''
    )

    return index === -1
      ? Number.MAX_SAFE_INTEGER
      : index
  }

  const generationA = generationIndex(a)
  const generationB = generationIndex(b)

  if (generationA !== generationB) {
    return generationA - generationB
  }

  const parts = (booster: BoosterSet) => {
    const match = booster.code?.match(
      /(?:^|-)([A-Z]+)0*(\d+)$/i
    )

    return {
      family: match?.[1] ?? booster.code ?? '',
      number: Number(match?.[2] ?? Number.MAX_SAFE_INTEGER),
    }
  }

  const partsA = parts(a)
  const partsB = parts(b)
  const familyOrder = setCodeCollator.compare(
    partsA.family,
    partsB.family
  )

  if (familyOrder !== 0) {
    return familyOrder
  }

  if (partsA.number !== partsB.number) {
    return partsA.number - partsB.number
  }

  return setCodeCollator.compare(
    a.code ?? a.name,
    b.code ?? b.name
  )
}

/**
 * Estos son los sets que finalmente renderiza el desplegable de la plantilla.
 * El store entrega el catálogo; aquí solo se filtra y ordena para la vista.
 */
const visibleBoosterSets = computed(() =>
  props.boosterSets
    .filter(
      booster =>
        local.value.generation === 'all' ||
        booster.generation === local.value.generation
    )
    .sort(compareBoosterSets)
)

const selectedBoosterLabel = computed(() => {
  if (props.boosterSetsLoading) {
    return 'Cargando sets...'
  }

  if (local.value.boosterSet === 'all') {
    return 'All'
  }

  const selected = props.boosterSets.find(
    booster => booster.url === local.value.boosterSet
  )

  return selected
    ? boosterLabel(selected)
    : 'All'
})

const submitSearch = () => {
  emit('search', {
    ...local.value,
  })
}

watch(
  local,
  value => {
    emit('update:filters', {
      ...value,
    })
  },
  { deep: true }
)

watch(
  () => local.value.generation,
  () => {
    const currentBoosterIsVisible =
      visibleBoosterSets.value.some(
        booster => booster.url === local.value.boosterSet
      )

    if (
      local.value.boosterSet !== 'all' &&
      !currentBoosterIsVisible
    ) {
      local.value.boosterSet = 'all'
    }
  }
)
</script>

<template>
  <section class="bg-card border border-border rounded-lg p-4">
    <div
      class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr] gap-x-10 gap-y-2"
    >
      <!-- SEARCH -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Buscar
        </span>

        <input
          v-model="local.search"
          type="text"
          placeholder="Nombre, número, nación..."
          class="flex-1 h-9 px-3 text-sm bg-muted rounded-md border border-border outline-none focus:ring-2 focus:ring-ring"
        >
      </div>

      <!-- GENERATION -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Gen
        </span>

        <ToggleGroup
          v-model="local.generation"
          type="single"
          variant="outline"
          size="sm"
        >
          <ToggleGroupItem
            v-for="generation in GENERATIONS"
            :key="generation.value"
            :value="generation.value"
          >
            {{ generation.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- SET -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Set
        </span>

        <Popover v-model:open="boosterOpen">
          <PopoverTrigger as-child>
            <button
              type="button"
              class="flex-1 flex justify-between gap-3 px-3 py-2 text-sm bg-muted rounded-md border border-border text-left disabled:opacity-50"
              :disabled="boosterSetsLoading"
            >
              <span
                class="min-w-0 flex-1 truncate whitespace-nowrap"
                :title="selectedBoosterLabel"
              >
                {{ selectedBoosterLabel }}
              </span>

              <span class="shrink-0 opacity-50">⌕</span>
            </button>
          </PopoverTrigger>

          <PopoverContent
            class="w-[min(34rem,calc(100vw-2rem))] p-0"
          >
            <Command>
              <CommandInput placeholder="Buscar booster set..." />

              <CommandEmpty>
                No se encontraron sets para esta generación.
              </CommandEmpty>

              <div class="max-h-72 overflow-y-auto">
                <CommandGroup>
                  <CommandItem
                    value="all"
                    @select="() => {
                      local.boosterSet = 'all'
                      boosterOpen = false
                    }"
                  >
                    All
                  </CommandItem>

                  <CommandItem
                    v-for="booster in visibleBoosterSets"
                    :key="booster.url"
                    :value="boosterLabel(booster)"
                    class="grid grid-cols-[max-content_minmax(0,1fr)] items-center gap-3"
                    @select="() => {
                      local.boosterSet = booster.url
                      boosterOpen = false
                    }"
                  >
                    <span class="font-medium whitespace-nowrap">
                      {{ booster.code }}
                    </span>

                    <span
                      class="min-w-0 truncate whitespace-nowrap text-muted-foreground"
                      :title="booster.name"
                    >
                      {{ booster.name }}
                    </span>
                  </CommandItem>
                </CommandGroup>
              </div>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <!-- NATION -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Nation
        </span>

        <Select v-model="local.nation">
          <SelectTrigger class="flex-1">
            <SelectValue />
          </SelectTrigger>

          <SelectContent>
            <SelectItem
              v-for="nation in NATIONS"
              :key="nation.value"
              :value="nation.value"
            >
              {{ nation.label }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- CLAN -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Clan
        </span>

        <Popover v-model:open="clanOpen">
          <PopoverTrigger as-child>
            <button
              type="button"
              class="flex-1 flex justify-between px-3 py-2 text-sm bg-muted rounded-md border border-border"
            >
              {{ local.clan === 'all' ? 'All' : local.clan }}
              <span class="opacity-50">⌕</span>
            </button>
          </PopoverTrigger>

          <PopoverContent class="p-0">
            <Command>
              <CommandInput placeholder="Buscar clan..." />
              <CommandEmpty>No encontrado.</CommandEmpty>

              <div class="max-h-64 overflow-y-auto">
                <CommandGroup>
                  <CommandItem
                    value="all"
                    @select="() => {
                      local.clan = 'all'
                      clanOpen = false
                    }"
                  >
                    All
                  </CommandItem>

                  <CommandItem
                    v-for="clan in availableClans"
                    :key="clan"
                    :value="clan"
                    @select="() => {
                      local.clan = clan
                      clanOpen = false
                    }"
                  >
                    {{ clan }}
                  </CommandItem>
                </CommandGroup>
              </div>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <!-- TYPE -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Type
        </span>

        <ToggleGroup
          v-model="local.type"
          type="single"
          variant="outline"
          size="sm"
        >
          <ToggleGroupItem
            v-for="type in TYPES"
            :key="type.value"
            :value="type.value"
          >
            {{ type.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- GRADE -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Grade
        </span>

        <ToggleGroup
          v-model="local.grade"
          type="single"
          variant="outline"
          size="sm"
        >
          <ToggleGroupItem
            v-for="grade in GRADES"
            :key="grade.value"
            :value="grade.value"
          >
            {{ grade.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- TRIGGER -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">
          Trigger
        </span>

        <ToggleGroup
          v-model="local.trigger"
          type="single"
          variant="outline"
          size="sm"
        >
          <ToggleGroupItem
            v-for="trigger in TRIGGERS"
            :key="trigger.value"
            :value="trigger.value"
          >
            {{ trigger.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>

    <div
      class="mt-4 pt-4 border-t border-border flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
    >
      <p
        v-if="!canSearch"
        class="text-xs text-muted-foreground"
      >
        {{ searchDisabledReason }}
      </p>

      <p
        v-else
        class="text-xs text-muted-foreground"
      >
        La búsqueda se aplicará al pulsar el botón.
      </p>

      <button
        type="button"
        class="h-9 px-5 rounded-md bg-primary text-primary-foreground text-sm font-medium transition-opacity disabled:opacity-50"
        :disabled="!canSearch || searching || boosterSetsLoading"
        @click="submitSearch"
      >
        {{ searching ? 'Cargando...' : 'Buscar' }}
      </button>
    </div>

    <p class="mt-3 text-xs text-muted-foreground">
      Grade, Nation, Type y Trigger usan los datos normalizados de las cartas. Clan y texto libre consultan el índice disponible.
    </p>
  </section>
</template>
