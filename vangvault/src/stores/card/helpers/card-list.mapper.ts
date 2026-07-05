import type { BoosterSet } from '@/models/booster.model'
import type { CardEntry } from '@/models/card-entry.model'
import type { ScrapedCardListRow } from './card-list.extractor'

const NATION_KEYS: Record<string, string> = {
  'dragon empire': 'dragon_empire',
  stoicheia: 'stoicheia',
  'dark states': 'dark_states',
  'keter sanctuary': 'keter',
  'brandt gate': 'brandt',
  'lyrical monasterio': 'lyrical',
}

const mapNationToKey = (
  nation?: string
): string | undefined => {
  if (!nation) return undefined

  return NATION_KEYS[nation.toLowerCase()]
}

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
    rarity: row.rarity,
  }))
}