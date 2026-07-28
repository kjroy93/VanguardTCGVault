import type { BoosterSet } from '@/models/booster.model'
import { fetchWikiPageHtml } from '@/services/wiki/wiki.client'

/**
 * FETCH DE CARTAS
 * ---------------
 * Recibe el `BoosterSet` elegido por el usuario y descarga el HTML de su URL.
 * No interpreta la tabla: `card-list.extractor.ts` se ocupa del siguiente paso.
 */
export const fetchBoosterSetCardListHtml = (
  booster: BoosterSet
): Promise<string> => {
  return fetchWikiPageHtml(booster.url)
}
