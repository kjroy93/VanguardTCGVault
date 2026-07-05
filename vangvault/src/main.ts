import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import './style.css'

document.documentElement.classList.add('dark')

createApp(App)
.use(createPinia())
.use(router)

.mount('#app')


