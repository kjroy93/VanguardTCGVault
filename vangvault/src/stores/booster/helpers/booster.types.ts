/**
 * RESPONSABILIDAD:
 * Definir tipos internos utilizados durante el parsing y la evaluación de reglas.
 *
 * CONTEXTO:
 * - Tipos auxiliares para lógica interna (parser / rules)
 * - No forman parte del modelo de dominio
 *
 * SALIDA:
 * - Tipos TypeScript reutilizables dentro del módulo booster
 *
 * NO HACE:
 * - No representa datos finales de la aplicación
 * - No se usa en UI ni en stores directamente
 */

/**
 * Contexto construido a partir del nombre crudo del booster, utilizado para aplicar reglas de negocio.
 */
export type BoosterParseContext = {
  rawName: string
  code?: string
  parts: string[]
  head: string
  seg: string
}

/**
 * Tipo genérico para definir reglas de negocio que resuelven un valor a partir del contexto.
 */
export type Rule<T> = {
  when: (ctx: BoosterParseContext) => boolean
  resolve: (ctx: BoosterParseContext) => T
}

/**
 * TAGS
 * ----
 * Fuente única de verdad para las categorías de boosters.
 *
 * Cada entrada contiene:
 * - id: valor interno usado en lógica (grouping, rules, keys…)
 * - label: texto mostrado en UI
 *
 * ⚠️ IMPORTANTE:
 * - No usar strings sueltos en el proyecto (usar siempre TAGS.X.id)
 * - Si añades un tag, hazlo aquí → afecta a UI y lógica automáticamente
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

/**
 * Tag
 * ---
 * Tipo derivado automáticamente de TAGS.
 *
 * Representa el valor interno (id), no la clave (V, G, etc).
 *
 * Ejemplo:
 * - válido: "V", "D", "Original"
 * - NO válido: "v", "generation"
 */
export type Tag = typeof TAGS[keyof typeof TAGS]['id']

/**
 * getTagLabel
 * -----------
 * Devuelve la etiqueta de UI asociada a un tag.
 *
 * @param tag Tag interno (id)
 * @returns Texto legible para UI
 *
 * Uso típico:
 * {{ getTagLabel(cat) }}
 */
export const getTagLabel = (tag: Tag) =>
	Object.values(TAGS).find(t => t.id === tag)?.label ?? tag