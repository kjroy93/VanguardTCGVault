import type { CardEntry } from '@/models/card-entry.model'
import type {
  CardDetail,
  CardFilterType,
  CardTrigger,
} from '@/models/card-detail.model'

import {
  fetchWikiApiJson,
  getWikiPageTitleFromUrl,
} from '@/services/wiki/wiki.client'

type WikiParseTextResponse = {
  parse?: {
    title?: string
    text?:
      | string
      | {
          '*': string
        }
  }
}

type CardMetadata = Record<string, string>

/** Tiempo máximo que esperamos por la ficha de una carta. */
const DETAIL_TIMEOUT_MS = 12_000

/** Limpia un texto que debe permanecer en una sola línea. */
const cleanInlineText = (
  value?: string | null
): string =>
  (value ?? '')
    .replace(/\s+/g, ' ')
    .trim()

/**
 * Prepara textos para comparaciones internas: minúsculas, sin signos y con
 * espacios uniformes.
 */
const normalizeText = (
  value?: string | null
): string =>
  cleanInlineText(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

/**
 * Compite una promesa real contra un temporizador.
 *
 * Si la wiki no responde antes del límite, rechaza la operación para que la
 * interfaz no quede cargando eternamente.
 */
const withTimeout = async <T>(
  promise: Promise<T>,
  label: string
): Promise<T> => {
  let timeoutId: number | undefined

  const timeout = new Promise<T>((_, reject) => {
    timeoutId = window.setTimeout(() => {
      reject(
        new Error(
          `La wiki tardó demasiado al cargar ${label}`
        )
      )
    }, DETAIL_TIMEOUT_MS)
  })

  try {
    return await Promise.race([
      promise,
      timeout,
    ])
  } finally {
    if (timeoutId !== undefined) {
      window.clearTimeout(timeoutId)
    }
  }
}

/**
 * MediaWiki puede devolver `parse.text` como string o dentro de la propiedad
 * `*`. Esta función oculta esa diferencia al resto del fichero.
 */
const getParseHtml = (
  response: WikiParseTextResponse
): string | undefined => {
  const text = response.parse?.text

  if (typeof text === 'string') {
    return text
  }

  if (text && typeof text === 'object') {
    return text['*']
  }

  return undefined
}

/**
 * Descarga el HTML completo de la ficha de una carta y sigue redirecciones.
 */
const fetchCardPageHtml = async (
  card: CardEntry
): Promise<string> => {
  const pageTitle = getWikiPageTitleFromUrl(
    card.wikiUrl
  )

  const response = await withTimeout(
    fetchWikiApiJson<WikiParseTextResponse>({
      action: 'parse',
      page: pageTitle,
      prop: 'text',
      redirects: '1',
      formatversion: '2',
    }),
    card.cardNumber
  )

  const html = getParseHtml(response)

  if (!html) {
    throw new Error(
      `La wiki no devolvió HTML para ${card.name}`
    )
  }

  return html
}

/** Reconoce los distintos textos que la wiki usa para titular los efectos. */
const isCardEffectHeading = (
  value?: string | null
): boolean => {
  const normalized = normalizeText(value)

  return (
    normalized === 'card effects' ||
    normalized === 'card effect' ||
    normalized.includes('card effect')
  )
}

/**
 * Recorre recursivamente un nodo HTML conservando saltos de línea útiles.
 *
 * `textContent` puro mezclaría párrafos, costes y habilidades en una sola
 * línea, dificultando su lectura posterior.
 */
const extractTextWithLineBreaks = (
  node: Node
): string => {
  if (node.nodeType === Node.TEXT_NODE) {
    return node.textContent ?? ''
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return ''
  }

  const element = node as HTMLElement
  const tag = element.tagName.toLowerCase()

  if (tag === 'br') {
    return '\n'
  }

  const blockTags = new Set([
    'p',
    'div',
    'li',
    'tr',
    'section',
    'article',
  ])

  const content = Array.from(element.childNodes)
    .map(extractTextWithLineBreaks)
    .join('')

  return blockTags.has(tag)
    ? `${content}\n`
    : content
}

/**
 * Limpia el efecto sin destruir su separación en párrafos.
 */
const normalizeEffectText = (
  value: string
): string => {
  const lines = value
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .map(line =>
      line
        .replace(/[ \t]+/g, ' ')
        .trim()
    )

  const result: string[] = []
  let previousWasEmpty = false

  for (const line of lines) {
    const isEmpty = line.length === 0

    if (isEmpty) {
      if (!previousWasEmpty && result.length > 0) {
        result.push('')
      }

      previousWasEmpty = true
      continue
    }

    result.push(line)
    previousWasEmpty = false
  }

  return result.join('\n').trim()
}

/**
 * Localiza la tabla de efectos y reúne las filas situadas bajo su cabecera.
 */
const extractCardEffectFromHtml = (
  html: string
): string | undefined => {
  const doc = new DOMParser().parseFromString(
    html,
    'text/html'
  )

  const tables = Array.from(
    doc.querySelectorAll<HTMLTableElement>('table')
  )

  const effectTable = tables.find(table => {
    if (table.classList.contains('effect')) {
      return true
    }

    return isCardEffectHeading(
      table.querySelector('th')?.textContent
    )
  })

  if (!effectTable) {
    return undefined
  }

  const rows = Array.from(
    effectTable.querySelectorAll<HTMLTableRowElement>(
      'tr'
    )
  )

  const headingRowIndex = rows.findIndex(row =>
    isCardEffectHeading(
      row.querySelector('th')?.textContent
    )
  )

  if (headingRowIndex === -1) {
    return undefined
  }

  const parts: string[] = []

  for (
    let index = headingRowIndex + 1;
    index < rows.length;
    index += 1
  ) {
    const row = rows[index]

    if (row.querySelector('th')) {
      break
    }

    const cells = Array.from(
      row.querySelectorAll<HTMLTableCellElement>('td')
    )

    for (const cell of cells) {
      const text = normalizeEffectText(
        extractTextWithLineBreaks(cell)
      )

      if (text) {
        parts.push(text)
      }
    }
  }

  const effect = [...new Set(parts)]
    .join('\n\n')
    .trim()

  return effect || undefined
}

/**
 * La ficha de Fandom usa filas del estilo:
 *
 * <tr>
 *   <td>Card Type</td>
 *   <td>Trigger Unit</td>
 * </tr>
 *
 * Por tanto, la primera celda es la etiqueta y la segunda
 * contiene el valor. No hay que depender de <th>.
 */
const extractCardMetadataFromHtml = (
  html: string
): CardMetadata => {
  const doc = new DOMParser().parseFromString(
    html,
    'text/html'
  )

  const metadata: CardMetadata = {}

  const infoRows = Array.from(
    doc.querySelectorAll<HTMLTableRowElement>(
      '.info-main table tr, .info-extra table tr'
    )
  )

  for (const row of infoRows) {
    const cells = Array.from(row.children).filter(
      (
        cell
      ): cell is HTMLTableCellElement | HTMLTableHeaderCellElement =>
        cell.tagName === 'TD' ||
        cell.tagName === 'TH'
    )

    if (cells.length < 2) {
      continue
    }

    const key = normalizeText(cells[0].textContent)

    const value = cleanInlineText(
      cells
        .slice(1)
        .map(cell => cell.textContent ?? '')
        .join(' ')
    )

    if (!key || !value || metadata[key]) {
      continue
    }

    metadata[key] = value
  }

  return metadata
}

const getMetadataValue = (
  metadata: CardMetadata,
  keys: string[]
): string | undefined => {
  /**
   * Recorremos alternativas en orden de preferencia porque distintas fichas
   * pueden llamar de forma diferente al mismo campo.
   */
  for (const key of keys) {
    const value = metadata[key]

    if (value) {
      return value
    }
  }

  return undefined
}

/** Convierte el texto libre de `Card Type` en una opción de filtro estable. */
const resolveCardType = (
  cardTypeText?: string
): CardFilterType | undefined => {
  const value = normalizeText(cardTypeText)

  if (!value) {
    return undefined
  }

  if (value.includes('trigger')) {
    return 'trigger'
  }

  if (value.includes('blitz')) {
    return 'blitz'
  }

  if (value.includes('order')) {
    return 'order'
  }

  if (value.includes('unit')) {
    return 'unit'
  }

  return undefined
}

/** Convierte el texto de trigger de la wiki en una opción de filtro estable. */
const resolveTrigger = (
  triggerEffectText?: string
): CardTrigger | undefined => {
  const value = normalizeText(triggerEffectText)

  if (!value) {
    return undefined
  }

  if (value.includes('over')) {
    return 'over'
  }

  if (value.includes('critical')) {
    return 'critical'
  }

  if (value.includes('draw')) {
    return 'draw'
  }

  if (value.includes('front')) {
    return 'front'
  }

  if (value.includes('heal')) {
    return 'heal'
  }

  return undefined
}

/**
 * Orquesta la carga de detalle de una carta.
 *
 * Descarga una sola ficha, extrae sus metadatos y devuelve el modelo pequeño
 * que guardará `card.store.ts`.
 */
export const fetchCardDetail = async (
  card: CardEntry
): Promise<CardDetail> => {
  const html = await fetchCardPageHtml(card)

  const metadata = extractCardMetadataFromHtml(html)

  const cardTypeText = getMetadataValue(metadata, [
    'card type',
  ])

  const triggerEffectText = getMetadataValue(metadata, [
    'trigger effect',
    'trigger',
    'trigger icon',
    'trigger type',
  ])

  const detail: CardDetail = {
    cardId: card.id,
    effectEn: extractCardEffectFromHtml(html),

    clan: getMetadataValue(metadata, [
      'clan',
    ]),

    cardType: resolveCardType(cardTypeText),

    trigger: resolveTrigger(triggerEffectText),
  }

  /**
   * Este log es diagnóstico: permite comparar el texto original de Fandom con
   * los valores normalizados si un filtro no reconoce una carta.
   */
  console.debug('[Card metadata parsed]', {
    cardNumber: card.cardNumber,
    name: card.name,
    cardTypeText,
    triggerEffectText,
    cardType: detail.cardType,
    trigger: detail.trigger,
    clan: detail.clan,
  })

  return detail
}
