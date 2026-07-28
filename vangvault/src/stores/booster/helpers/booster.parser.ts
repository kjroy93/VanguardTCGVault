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

const SPECIAL_SERIES_TITLE_PATTERN =
  /^(?:(P&V|DZ|D|V|G)\s+)?Special Series\s+0*(\d+)\b/i

/**
 * Construye una versión fácil de analizar del nombre recibido.
 *
 * Ejemplo:
 * `VGE-DZ-SS11: Festival Booster 2025`
 * se divide en código, cabecera `VGE` y segmentos `DZ`, `SS11`.
 *
 * Para títulos sin código, como `DZ Special Series 16`, también fabrica el
 * código normalizado `DZ-SS16`.
 */
function buildCtx(rawName: string): Ctx {
  const codeMatch = rawName.match(/^([A-Z0-9]+(?:[-:][A-Z0-9]+)*)\b/i)
  const specialSeriesMatch = rawName.match(
    SPECIAL_SERIES_TITLE_PATTERN
  )

  const matchedCode =
    codeMatch?.[1].includes('-')
      ? codeMatch[1]
      : undefined

  const code = (
    matchedCode ??
    (
      specialSeriesMatch
        ? `${specialSeriesMatch[1] ? `${specialSeriesMatch[1]}-` : ''}SS${specialSeriesMatch[2].padStart(2, '0')}`
        : codeMatch?.[1]
    )
  )?.toUpperCase()

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
 * Recorre una lista de reglas y usa la primera que coincida.
 *
 * `T` representa el tipo de resultado que esperamos obtener. Si ninguna regla
 * se cumple, se ejecuta `fallback` para devolver un valor seguro.
 */
function resolveByRules<T>(ctx: Ctx, rules: Rule<T>[], fallback: (ctx: Ctx) => T): T {
  const match = rules.find(r => r.when(ctx))
  return match ? match.resolve(ctx) : fallback(ctx)
}

/**
 * Reglas que convierten distintos formatos de código en una generación.
 *
 * Están separadas del parser principal para que cada caso se pueda leer y
 * modificar sin crear una cadena grande de `if/else`.
 */
const generationRules: Rule<string | undefined>[] = [
  {
    /** Títulos descriptivos como `DZ Special Series 16`. */
    when: ctx =>
      [TAGS.G.id, TAGS.V.id, TAGS.D.id, TAGS.DZ.id]
        .includes(ctx.head as 'G' | 'V' | 'D' | 'DZ') &&
      /^SS\d+/i.test(ctx.seg),
    resolve: ctx => ctx.head
  },
  {
    when: ctx => ctx.head === 'VGE',
    resolve: () => TAGS.VGE.id
  },
  {
    /** `VG-G`, `VG-V`, `VG-D` y `VG-DZ` toman el segundo segmento. */
    when: ctx =>
      ctx.head === 'VG' &&
      !!ctx.seg &&
      /** `BT` y `LBT` no son generaciones. */
      !/^L?BT/i.test(ctx.seg),
    resolve: ctx => ctx.seg
  },
  {
    /** Los códigos `VG-BT` pertenecen a la serie Original. */
    when: ctx =>
      ctx.head === 'VG' &&
      (/^L?BT/i.test(ctx.seg || '') || !ctx.seg),
    resolve: () => TAGS.ORIGINAL.id
  }
]

/**
 * Excepciones que deben aplicarse antes de las reglas generales.
 *
 * `VGE` indica una variante regional, pero `VGE-DZ` sigue perteneciendo a la
 * generación DZ. Sin esta excepción quedaría clasificado como generación VGE.
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
  /**
   * A partir de aquí no se consulta la red: solo se transforma texto.
   * El resultado final es el modelo que almacenará Pinia y utilizará la UI.
   */
  const ctx = buildCtx(rawName)

  /** Tipo de dato que puede producir una regla de excepción. */
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

  /**
   * Extrae el número del producto. Para BT se busca expresamente `BTxx`;
   * para el resto se toma el primer número presente en el código.
   */
  const btMatch = ctx.code?.match(/BT0*(\d+)/i)
  const number = btMatch
    ? btMatch[1]
    : ctx.code?.match(/\d+/)?.[0]

  /**
   * Elimina el código y los separadores del texto visible.
   * Conserva únicamente un nombre como `Festival Booster 2025`.
   */
  const cleanName =
    rawName
      .replace(
        SPECIAL_SERIES_TITLE_PATTERN,
        ''
      )
      .replace(
        /^([A-Z0-9]+(?:[-:][A-Z0-9]+)*)\s*[:\-–—]?\s*/i,
        ''
      )
      .replace(/^\s*[:\-–—]\s*/, '')
      .trim() ||
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
