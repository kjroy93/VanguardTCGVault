/**
 * RESPONSABILIDAD:
 * Fuente única de verdad para las categorías (tags) de boosters.
 *
 * CONTEXTO:
 * - Define valores usados tanto en lógica como en UI
 * - Evita el uso de strings sueltos en el proyecto
 *
 * ENTRADA:
 * - No recibe datos (constante global del dominio)
 *
 * SALIDA:
 * - TAGS: definición de etiquetas
 * - Tag: tipo derivado (id interno)
 * - getTagLabel: helper para UI
 */

/**
 * @brief Fuente única de verdad para las categorías (tags) de boosters.+
 * Cada entrada contiene:
 * - id: valor interno usado en lógica (grouping, rules, keys…)
 * - label: texto mostrado en UI
 */

export const TAGS = {
  V: { id: 'V', label: 'V' },
  G: { id: 'G', label: 'G (Generation)' },
  D: { id: 'D', label: 'D' },
  DZ: { id: 'DZ', label: 'DZ' },
  VGE: { id: 'VGE', label: 'VGE' },
  T: { id: 'T', label: 'Thai' },
  WORLDWIDE: { id: 'Worldwide', label: 'Worldwide' },
  OTHER: { id: 'Otros', label: 'Otros' },
  ORIGINAL: { id: 'Original', label: 'Original' }
} as const

export type Tag = typeof TAGS[keyof typeof TAGS]['id']

/**
 * @brief Devuelve la etiqueta de UI asociada a un tag.
 * @param tag Tag interno (id)
 * @returns Texto legible para UI
 */
export const getTagLabel = (tag: Tag) =>
  Object.values(TAGS).find(t => t.id === tag)?.label ?? tag