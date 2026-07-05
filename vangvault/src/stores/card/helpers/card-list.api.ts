import type { BoosterSet } from '@/models/booster.model'
import { fetchWikiPageHtml } from '@/services/wiki/wiki.client'

export const fetchBoosterSetCardListHtml = (
  booster: BoosterSet
): Promise<string> => {
  return fetchWikiPageHtml(booster.url)
}