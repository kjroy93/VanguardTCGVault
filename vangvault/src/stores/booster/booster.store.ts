/**
 * RESPONSABILIDAD:
 * Orquestar la obtención, transformación y almacenamiento de boosters en el estado global.
 *
 * CONTEXTO:
 * - Coordina:
 *   - API (fetch)
 *   - Parser (extracción)
 *   - Rules (lógica de negocio)
 *   - Grouper (organización)
 * - Mantiene el estado reactivo para la UI
 *
 * ENTRADA:
 * - Acciones invocadas desde la UI
 *
 * SALIDA:
 * - Estado actualizado:
 *   - sets (lista de boosters)
 *   - grouped (boosters agrupados)
 *   - loading (estado de carga)
 */
import { defineStore } from 'pinia'
import { BoosterSet } from '@/models/booster.model'
import { fetchWikiBoosterHtml } from '@/stores/booster/helpers/booster.api'
import { extractBoosters } from './helpers/booster.extractor'
import { parseBoosterFromScraped } from './helpers/booster.parser'

export const useBoosterStore = defineStore('booster', {
  state: () => ({
    sets: [] as BoosterSet[],
    grouped: {} as Record<string, BoosterSet[]>,
    loading: false
  }),

  actions: {
    /**
     * @brief carga completa de boosters desde la fuente (fetch + parse + group)
     */
    async loadFromApi(): Promise<BoosterSet[]> {
      this.loading = true

      try {
        const html = await fetchWikiBoosterHtml()
        const items = extractBoosters(html)
        const boosters = items.map(i => parseBoosterFromScraped(i.name, i.url) as BoosterSet)
        this.sets = boosters
        return boosters
      } finally {
        this.loading = false
      }
    }
  }
})