<script setup lang="ts">
import { onMounted } from 'vue'
import { useBoosterStore } from '@/stores/booster/booster.store'
const boosterStore = useBoosterStore()

onMounted(async () => {
  await boosterStore.loadFromApi()

console.log([...boosterStore.sets])
})
</script>

<template>
  <main class="p-4">
    <h1 class="text-2xl font-bold mb-4">
      Boosters
    </h1>

    <div v-if="boosterStore.loading">
      Cargando...
    </div>

    <ul v-else class="space-y-2">
      <li
        v-for="booster in boosterStore.sets"
        :key="booster.url"
      >
        <a
          :href="booster.url"
          target="_blank"
          class="text-blue-400 hover:underline"
        >
          [{{ booster.generation }}]
          {{ booster.code }}
          —
          {{ booster.name }}
        </a>
      </li>
    </ul>
  </main>
  <router-view />
</template>