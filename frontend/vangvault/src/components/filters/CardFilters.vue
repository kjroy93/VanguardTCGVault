<script setup lang="ts">
import { ref, watch, computed } from 'vue'

import {
  TagsInput,
  TagsInputInput,
  TagsInputItem,
  TagsInputItemText,
  TagsInputItemDelete,
} from '@/components/ui/tags-input'

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

// 🔹 TIPADO
type Filters = {
  search: string
  grade: string
  nation: string
  clan: string
  type: string
  trigger: string
  generation: string
}

// 🔹 CONFIG
const GENERATIONS = [
  { label: 'All', value: 'all' },
  { label: 'Original', value: 'OG' },
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

// 🔹 PROPS
const props = defineProps<{ filters: Filters }>()

const emit = defineEmits<{
  (e: 'update:filters', value: Filters): void
}>()

// 🔹 STATE
const local = ref<Filters>({
  search: '',
  grade: 'all',
  nation: 'all',
  clan: 'all',
  type: 'all',
  trigger: 'all',
  generation: 'all',
})

const searchTags = ref<string[]>([])

// 🔹 BOOSTER SETS (for generation filter)
/*const { boosterSets } = useBoosterSets()*/
/*const filteredBoosters = computed(() => {
  if (local.value.generation === 'all') return boosterSets.value

  return boosterSets.value.filter(
    b => b.generation === local.value.generation
  )
})*/



// 🔹 CLANES FILTRADOS
const availableClans = computed(() => {
  if (local.value.nation === 'all') return CLANS.map(c => c.name)

  return CLANS
    .filter(c => c.nation === local.value.nation || c.nation === null)
    .map(c => c.name)
})

// 🔹 TAG INPUT
const handleTagInput = (e: KeyboardEvent) => {
  if (e.key === ';') {
    e.preventDefault()
    const input = e.target as HTMLInputElement
    const value = input.value.trim().toLowerCase()

    if (value && !searchTags.value.includes(value)) {
      searchTags.value.push(value)
    }

    input.value = ''
  }
}

// 🔹 SYN

const open = ref(false)
</script>

<template>
  <div class="bg-card border border-border rounded-lg p-4">

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr] gap-y-1 gap-x-10">
 
      <!-- SEARCH -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Buscar</span>

        <TagsInput v-model="searchTags" class="flex-1  p-2">
          <TagsInputItem v-for="item in searchTags" :key="item" :value="item">
            <TagsInputItemText />
            <TagsInputItemDelete />
          </TagsInputItem>

          <TagsInputInput
            placeholder="Buscar (;)"
            @keydown.enter.prevent
            @keydown="handleTagInput"
          />
        </TagsInput>
      </div>

      <!-- GENERACIÓN -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Gen</span>

        <ToggleGroup type="single" v-model="local.generation" variant="outline" size="sm">
          <ToggleGroupItem v-for="g in GENERATIONS" :key="g.value" :value="g.value">
            {{ g.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- NATION -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Nation</span>

        <Select v-model="local.nation">
          <SelectTrigger class="flex-1">
            <SelectValue />
          </SelectTrigger>

          <SelectContent>
            <SelectItem v-for="n in NATIONS" :key="n.value" :value="n.value">
              {{ n.label }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- CLAN -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Clan</span>

        <Popover v-model:open="open">
          <PopoverTrigger as-child>
            <button class="flex-1 flex justify-between px-3 py-2 text-sm bg-muted rounded-md border border-border">
              {{ local.clan === 'all' ? 'All' : local.clan }}
              <span class="opacity-50">⌕</span>
            </button>
          </PopoverTrigger>

          <PopoverContent class=" p-0">
            <Command>
              <CommandInput placeholder="Buscar clan..." />
              <CommandEmpty>No encontrado.</CommandEmpty>

              <div class="max-h-64 overflow-y-auto">
              <CommandGroup>
                <CommandItem value="all" @select="() => { local.clan = 'all'; open = false }">
                  All
                </CommandItem>

                <CommandItem
                  v-for="c in availableClans"
                  :key="c"
                  :value="c"
                  @select="() => { local.clan = c; open = false }"
                >
                  {{ c }}
                </CommandItem>
              </CommandGroup>
              </div>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <!-- TYPE -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Type</span>

        <ToggleGroup type="single" v-model="local.type" variant="outline" size="sm">
          <ToggleGroupItem v-for="t in TYPES" :key="t.value" :value="t.value">
            {{ t.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- GRADE -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Grade</span>

        <ToggleGroup type="single" v-model="local.grade" variant="outline" size="sm">
          <ToggleGroupItem v-for="g in GRADES" :key="g.value" :value="g.value">
            {{ g.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- TRIGGER -->
      <div class="flex items-center">
        <span class="w-15 text-sm text-muted-foreground">Trigger</span>

        <ToggleGroup type="single" v-model="local.trigger" variant="outline" size="sm">
          <ToggleGroupItem v-for="t in TRIGGERS" :key="t.value" :value="t.value">
            {{ t.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

    </div>
  </div>
</template>