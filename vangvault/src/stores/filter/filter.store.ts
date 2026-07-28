import { defineStore } from 'pinia'

/**
 * Forma del antiguo estado de filtros.
 *
 * Se mantiene separado de `CardFilters.vue`; actualmente la pantalla principal
 * conserva sus filtros en la propia vista y este store no participa en ella.
 */
type LegacyFilterState = {
  booster: string | null
  nation: string | null
  power: number | null
  shield: number | null
}

/**
 * Crea un objeto nuevo con todos los filtros vacíos.
 *
 * Es una función en vez de una constante para que cada reinicio obtenga un
 * objeto independiente.
 */
const createDefaultState = (): LegacyFilterState => ({
  booster: null,
  nation: null,
  power: null,
  shield: null,
})

export const useFilterStore = defineStore('filter', {
  /** Estado inicial de este store legado. */
  state: (): LegacyFilterState => createDefaultState(),

  actions: {
    /**
     * Cambia un único filtro.
     *
     * El genérico `K` obliga a que `key` sea una propiedad válida y que
     * `value` tenga el tipo correspondiente a esa propiedad.
     */
    setFilter<K extends keyof LegacyFilterState>(
      key: K,
      value: LegacyFilterState[K],
    ) {
      this.$patch({
        [key]: value,
      } as Partial<LegacyFilterState>)
    },

    /**
     * Restaura todos los filtros a sus valores iniciales.
     */
    resetFilters() {
      this.$patch(createDefaultState())
    },
  },
})
