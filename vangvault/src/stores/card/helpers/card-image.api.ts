import type { CardEntry } from '@/models/card-entry.model'
import {
  fetchWikiApiJson,
  getWikiPageTitleFromUrl,
} from '@/services/wiki/wiki.client'

type WikiPageImagesResponse = {
  query?: {
    pages?: Array<{
      title: string
      thumbnail?: {
        source?: string
      }
    }>
  }
}

type WikiParseImagesResponse = {
  parse?: {
    title?: string
    images?: string[]
  }
}

type WikiFileInfoResponse = {
  query?: {
    pages?: Array<{
      title: string
      imageinfo?: Array<{
        thumburl?: string
        url?: string
      }>
    }>
  }
}

const IMAGE_BATCH_SIZE = 25
const FALLBACK_CONCURRENCY = 4

const chunk = <T>(items: T[], size: number): T[][] => {
  const result: T[][] = []

  for (let index = 0; index < items.length; index += size) {
    result.push(items.slice(index, index + size))
  }

  return result
}

const normalizePageTitleKey = (value: string): string =>
  value
    .replaceAll('_', ' ')
    .trim()
    .toLowerCase()

const normalizeFileKey = (value: string): string =>
  value
    .replace(/^File:/i, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')

const getCardNumberKey = (cardNumber: string): string =>
  cardNumber
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')

const ensureFileTitle = (value: string): string =>
  value.startsWith('File:')
    ? value
    : `File:${value}`

const fetchPrimaryImageUrls = async (
  cards: CardEntry[]
): Promise<Record<string, string>> => {
  const cardsByPageTitle = new Map<string, CardEntry[]>()
  const pageTitlesByKey = new Map<string, string>()

  for (const card of cards) {
    const pageTitle = getWikiPageTitleFromUrl(card.wikiUrl)
    const titleKey = normalizePageTitleKey(pageTitle)

    pageTitlesByKey.set(titleKey, pageTitle)

    const current = cardsByPageTitle.get(titleKey) ?? []
    current.push(card)

    cardsByPageTitle.set(titleKey, current)
  }

  const imageUrlsByCardId: Record<string, string> = {}

  for (const pageTitles of chunk(
    [...pageTitlesByKey.values()],
    IMAGE_BATCH_SIZE
  )) {
    const json = await fetchWikiApiJson<WikiPageImagesResponse>({
      action: 'query',
      prop: 'pageimages',
      piprop: 'thumbnail',
      pithumbsize: '360',
      titles: pageTitles.join('|'),
    })

    for (const page of json.query?.pages ?? []) {
      const imageUrl = page.thumbnail?.source

      if (!imageUrl) continue

      const matchingCards =
        cardsByPageTitle.get(
          normalizePageTitleKey(page.title)
        ) ?? []

      for (const card of matchingCards) {
        imageUrlsByCardId[card.id] = imageUrl
      }
    }
  }

  return imageUrlsByCardId
}

const fetchJapaneseFallbackImageUrls = async (
  cards: CardEntry[]
): Promise<Record<string, string>> => {
  const cardIdsByFileKey = new Map<string, string[]>()
  const fileTitlesByKey = new Map<string, string>()

  for (const cardsBatch of chunk(
    cards,
    FALLBACK_CONCURRENCY
  )) {
    const results = await Promise.all(
      cardsBatch.map(async card => {
        const pageTitle = getWikiPageTitleFromUrl(card.wikiUrl)

        const json = await fetchWikiApiJson<WikiParseImagesResponse>({
          action: 'parse',
          page: pageTitle,
          prop: 'images',
          redirects: '1',
        })

        const imageNames = json.parse?.images ?? []
        const cardNumberKey = getCardNumberKey(card.cardNumber)

        const selectedImage = imageNames.find(imageName =>
          normalizeFileKey(imageName).includes(cardNumberKey)
        )

        console.info(
          `[JP parse fallback] ${card.cardNumber}`,
          {
            pageTitle,
            imageCount: imageNames.length,
            selectedImage: selectedImage ?? 'NO MATCH',
            images: imageNames,
          }
        )

        return {
          card,
          selectedImage,
        }
      })
    )

    for (const { card, selectedImage } of results) {
      if (!selectedImage) continue

      const fileTitle = ensureFileTitle(selectedImage)
      const fileKey = normalizeFileKey(fileTitle)

      const ids = cardIdsByFileKey.get(fileKey) ?? []
      ids.push(card.id)

      cardIdsByFileKey.set(fileKey, ids)
      fileTitlesByKey.set(fileKey, fileTitle)
    }
  }

  const imageUrlsByCardId: Record<string, string> = {}

  for (const fileTitles of chunk(
    [...fileTitlesByKey.values()],
    IMAGE_BATCH_SIZE
  )) {
    const json = await fetchWikiApiJson<WikiFileInfoResponse>({
      action: 'query',
      prop: 'imageinfo',
      iiprop: 'url',
      iiurlwidth: '360',
      titles: fileTitles.join('|'),
    })

    for (const page of json.query?.pages ?? []) {
      const imageUrl =
        page.imageinfo?.[0]?.thumburl ??
        page.imageinfo?.[0]?.url

      if (!imageUrl) continue

      const cardIds = cardIdsByFileKey.get(
        normalizeFileKey(page.title)
      ) ?? []

      for (const cardId of cardIds) {
        imageUrlsByCardId[cardId] = imageUrl
      }
    }
  }

  return imageUrlsByCardId
}

export const fetchCardImageUrls = async (
  cards: CardEntry[]
): Promise<Record<string, string>> => {
  const primaryImageUrls = await fetchPrimaryImageUrls(cards)

  const cardsWithoutEnglishImage = cards.filter(
    card => !primaryImageUrls[card.id]
  )

  if (cardsWithoutEnglishImage.length === 0) {
    return primaryImageUrls
  }

  console.info(
    `Buscando ${cardsWithoutEnglishImage.length} imágenes japonesas mediante parse...`
  )

  const japaneseImageUrls =
    await fetchJapaneseFallbackImageUrls(
      cardsWithoutEnglishImage
    )

  return {
    ...primaryImageUrls,
    ...japaneseImageUrls,
  }
}