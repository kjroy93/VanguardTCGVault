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
import { FALLBACK_BOOSTER_ITEMS } from '@/stores/booster/data/booster-catalog.fallback'
import { fetchWikiBoosterHtmlPages } from '@/stores/booster/helpers/booster.api'
import {
  extractBoostersFromPages,
  mergeBoosterItems,
} from './helpers/booster.extractor'
import { parseBoosterFromScraped } from './helpers/booster.parser'

export const useBoosterStore = defineStore('booster', {
  /**
   * ESTADO DEL CATÁLOGO
   *
   * - `sets`: lista plana que consume el selector de la pantalla.
   * - `grouped`: espacio reservado para agrupaciones por generación.
   * - `loading`: permite a la interfaz mostrar que la carga sigue en curso.
   */
  state: () => ({
    sets: [] as BoosterSet[],
    grouped: {} as Record<string, BoosterSet[]>,
    loading: false
  }),

  actions: {
    /**
     * Flujo del catálogo:
     * 1. API: descarga HTML de las páginas índice.
     * 2. Extractor: obtiene pares `{ name, url }` y quita duplicados.
     * 3. Parser: normaliza cada par como `BoosterSet`.
     * 4. Store: guarda el resultado reactivo que lee `CardFilters.vue`.
     */
    async loadFromApi(): Promise<BoosterSet[]> {
      /**
       * Activamos `loading` antes de cualquier operación asíncrona.
       * El bloque `finally` garantiza que vuelva a `false`, haya éxito o error.
       */
      this.loading = true

      try {
        /**
         * El catálogo local se publica antes de esperar a la red. De este modo
         * el usuario puede abrir el selector aunque Fandom tarde o esté caído.
         */
        const fallbackBoosters =
          FALLBACK_BOOSTER_ITEMS.map(item =>
            parseBoosterFromScraped(
              item.name,
              item.url
            )
          )

        this.sets = fallbackBoosters
        this.loading = false

        const htmlPages = await fetchWikiBoosterHtmlPages()
        const remoteItems =
          extractBoostersFromPages(htmlPages)

        /**
         * La wiki tiene prioridad porque puede contener productos nuevos.
         * El catálogo local completa los que falten y evita que una caída de
         * Fandom deje el selector reducido únicamente a "All".
         */
        const items = mergeBoosterItems(
          remoteItems,
          FALLBACK_BOOSTER_ITEMS
        )

        const boosters = items.map(item =>
          parseBoosterFromScraped(
            item.name,
            item.url
          )
        )

        this.sets = boosters
        return boosters
      } finally {
        this.loading = false
      }
    }
  }
})
