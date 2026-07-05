import { createRouter, createWebHistory } from 'vue-router'

import CardsView from '@/views/CardsView.vue'
import CardDetailView from '@/views/CardDetailView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: CardsView },
    { path: '/card/:id', component: CardDetailView }
  ]
})