<script setup lang="ts">
defineProps<{ card: any }>()
</script>

<template>
  <div class="flex gap-4 p-4 rounded-lg border border-border bg-card">
    <div class="w-28">
      <img :src="card.image" class="rounded-md" />
    </div>

    <div class="flex-1">
      <h2>{{ card.name }}</h2>
    </div>
  </div>
</template>