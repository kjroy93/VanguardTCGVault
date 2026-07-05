<script setup lang="ts">
defineProps<{ card: any }>()
</script>

<template>
  <div class="group cursor-pointer">
    <div class="aspect-[5/7] bg-muted rounded-md overflow-hidden border border-border">
      <img :src="card.image" class="w-full h-full object-cover" />
    </div>

    <p class="text-xs mt-1 truncate text-muted-foreground">
      {{ card.name }}
    </p>
  </div>
</template>