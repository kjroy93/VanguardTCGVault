/**
 * RESPONSABILIDAD:
 * Extraer información básica desde el nombre scrapeado de un booster.
 *
 * CONTEXTO:
 * - Recibe texto ya obtenido (no hace fetch)
 * - No aplica reglas de negocio
 * - No accede a estado ni almacenamiento
 *
 * ENTRADA:
 * - Nombre original del booster (rawName)
 * - URL asociada
 *
 * SALIDA:
 * - Objeto base con:
 *   - name limpio
 *   - code
 *   - number
 *   - contexto de parsing (ctx)
 */

import { BoosterSet } from '@/models/booster.model'
import { Card } from '@/models/card.model'
import { TAGS } from './booster.types'

type Ctx = {
  rawName: string
  code?: string
  parts: string[]
  head: string
  seg: string
}

type Rule<T> = {
  when: (ctx: Ctx) => boolean
  resolve: (ctx: Ctx) => T
}

/**
 * Construye el contexto base a partir del nombre
 */
function buildCtx(rawName: string): Ctx {
  const codeMatch = rawName.match(/^([A-Z0-9]+(?:[-:][A-Z0-9]+)*)\b/i)
  const code = codeMatch ? codeMatch[1].toUpperCase() : undefined
  const parts = code ? code.split(/[-:]/) : []

  return {
    rawName,
    code,
    parts,
    head: parts[0] || '',
    seg: parts[1] || ''
  }
}

/**
 * Motor genérico de resolución por reglas
 */
function resolveByRules<T>(ctx: Ctx, rules: Rule<T>[], fallback: (ctx: Ctx) => T): T {
  const match = rules.find(r => r.when(ctx))
  return match ? match.resolve(ctx) : fallback(ctx)
}

/**
 * Reglas de generación
 */
const generationRules: Rule<string | undefined>[] = [
  {
    when: ctx => ctx.head === 'VGE',
    resolve: () => TAGS.VGE.id
  },
  {
    // 🔥 Solo generaciones reales (G, V, D, DZ...)
    when: ctx =>
      ctx.head === 'VG' &&
      !!ctx.seg &&
      !/^L?BT/i.test(ctx.seg), // excluye BT
    resolve: ctx => ctx.seg
  },
  {
    // 🔥 BT → Original
    when: ctx =>
      ctx.head === 'VG' &&
      (/^L?BT/i.test(ctx.seg || '') || !ctx.seg),
    resolve: () => TAGS.ORIGINAL.id
  }
]

/**
 * Regla especial: VGE-DZ → DZ
 */
const overrideRules: Rule<{ generation?: string; region?: string }>[] = [
  {
    when: ctx => ctx.head === 'VGE' && ctx.seg === 'DZ',
    resolve: () => ({
      generation: TAGS.DZ.id,
      region: TAGS.DZ.id
    })
  }
]

/**
 * Parsea un booster set desde nombre scrapeado sin usar if/else.
 *
 * @param rawName Nombre original del booster
 * @param url URL del booster
 * @param cards Cartas asociadas (opcional)
 */
export function parseBoosterFromScraped(
  rawName: string,
  url: string,
  cards: Card[] = []
): BoosterSet {

  const ctx = buildCtx(rawName)

  // override (si aplica)
  type OverrideResult = {
    generation?: string
    region?: string
  }

  const override = resolveByRules<OverrideResult>(
    ctx,
    overrideRules,
    () => ({})
  )

  const generation =
    override.generation ??
    resolveByRules(ctx, generationRules, () => TAGS.ORIGINAL.id)

  // número
  const btMatch = ctx.code?.match(/BT0*(\d+)/i)
  const number = btMatch
    ? btMatch[1]
    : ctx.code?.match(/\d+/)?.[0]

  // nombre limpio
  const cleanName =
    rawName.replace(/^([A-Z0-9]+(?:[-:][A-Z0-9]+)*)\s*[:\-–—]?\s*/i, '').trim() ||
    rawName

  return new BoosterSet(
    cleanName,
    url,
    cards,
    ctx.code,
    generation,
    number
  )
}