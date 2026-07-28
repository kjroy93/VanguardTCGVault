import type { BoosterSet } from '@/models/booster.model'
import type {
  CardEntry,
  CardKind,
  TriggerKind,
} from '@/models/card-entry.model'
import type { ScrapedCardListRow } from './card-list.extractor'

const NATION_KEYS: Record<string, string> = {
  'dragon empire': 'dragon_empire',
  stoicheia: 'stoicheia',
  'dark states': 'dark_states',
  'keter sanctuary': 'keter',
  'brandt gate': 'brandt',
  'lyrical monasterio': 'lyrical',
}

/**
 * Convierte el nombre de nación de la wiki en la clave utilizada por el filtro
 * de la interfaz.
 */
const mapNationToKey = (
  nation?: string
): string | undefined => {
  if (!nation) return undefined

  return NATION_KEYS[nation.toLowerCase()]
}

/**
 * Deja el valor de la columna Type preparado para comparaciones exactas.
 */
const normalizeListType = (
  listType?: string
): string =>
  (listType ?? '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()

/**
 * Normaliza `Critical`, `Critical Trigger`, etc. a una única clave estable.
 */
const mapListTypeToTriggerKind = (
  listType?: string
): TriggerKind | undefined => {
  const normalizedType = normalizeListType(listType)

  const triggerKinds: TriggerKind[] = [
    'draw',
    'critical',
    'front',
    'heal',
    'over',
    'stand',
  ]

  return triggerKinds.find(triggerKind =>
    new RegExp(`\\b${triggerKind}\\b`).test(
      normalizedType
    )
  )
}

/**
 * Convierte las variantes visibles de la wiki a las cuatro opciones del filtro.
 *
 * El orden de las condiciones es intencionado: `Normal Order` contiene la
 * palabra "Normal", pero debe clasificarse como order y no como unit.
 */
const mapListTypeToCardKind = (
  listType?: string
): CardKind | undefined => {
  const normalizedType = normalizeListType(listType)

  if (normalizedType.includes('blitz')) {
    return 'blitz'
  }

  if (normalizedType.includes('order')) {
    return 'order'
  }

  if (
    mapListTypeToTriggerKind(listType) ||
    normalizedType.includes('trigger')
  ) {
    return 'trigger'
  }

  if (
    normalizedType === 'normal' ||
    normalizedType.includes('normal unit') ||
    normalizedType.endsWith(' unit')
  ) {
    return 'unit'
  }

  return undefined
}

/**
 * Fabrica un id estable combinando set y número de carta.
 *
 * El id se usa como clave en cachés y en los `v-for` de Vue.
 */
const buildCardId = (
  setCode: string | undefined,
  setKey: string,
  cardNumber: string
): string => {
  const source = setCode ?? setKey

  return `${source}-${cardNumber}`
    .replace(/[^\w]+/g, '-')
    .toLowerCase()
}

export const mapCardListRowsToEntries = (
  rows: ScrapedCardListRow[],
  booster: BoosterSet
): CardEntry[] => {
  /**
   * FILAS NORMALIZADAS -> MODELO DE LA APP
   *
   * Añade a cada fila la generación y el set de procedencia, genera un id
   * estable y convierte el nombre visible de la nación en la clave del filtro.
   * Aquí ya no se hace ningún fetch ni se toca el estado.
   */
  const setKey = booster.url

  return rows.map(row => ({
    id: buildCardId(
      booster.code,
      setKey,
      row.cardNumber
    ),

    setKey,
    setCode: booster.code,
    generation: booster.generation,

    cardNumber: row.cardNumber,
    name: row.name,
    wikiUrl: row.wikiUrl,

    grade: row.grade,
    nation: row.nation,
    nationKey: mapNationToKey(row.nation),
    listType: row.listType,
    cardKind: mapListTypeToCardKind(row.listType),
    triggerKind:
      mapListTypeToTriggerKind(row.listType),
    rarity: row.rarity,
  }))
}
