import type { CardEntry } from '@/models/card-entry.model'
import {
  fetchWikiApiJson,
  getWikiPageTitleFromUrl,
} from '@/services/wiki/wiki.client'

type WikiPageImagesResponse = {
  query?: {
    normalized?: Array<{
      from: string
      to: string
    }>
    redirects?: Array<{
      from: string
      to: string
    }>
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

/**
 * Divide un array grande en grupos más pequeños.
 *
 * MediaWiki admite varios títulos por petición, pero no conviene construir una
 * URL enorme. Por eso las imágenes se consultan en lotes de 25.
 */
const chunk = <T>(items: T[], size: number): T[][] => {
  const result: T[][] = []

  for (let index = 0; index < items.length; index += size) {
    result.push(items.slice(index, index + size))
  }

  return result
}

/** Normaliza títulos de página para poder relacionar respuesta y carta. */
const normalizePageTitleKey = (value: string): string =>
  value
    .replaceAll('_', ' ')
    .trim()
    .toLowerCase()

/** Normaliza nombres de fichero ignorando `File:`, signos y mayúsculas. */
const normalizeFileKey = (value: string): string =>
  value
    .replace(/^File:/i, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')

/** Deja el número de carta en una forma comparable con nombres de imagen. */
const getCardNumberKey = (cardNumber: string): string =>
  cardNumber
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')

/**
 * Produce las variantes aceptables de un número.
 *
 * Por ejemplo, para `DZ-SS04/013EN` prueba la versión completa y otra sin el
 * sufijo regional `EN`.
 */
const getCardNumberKeys = (
  cardNumber: string
): string[] => {
  const fullKey = getCardNumberKey(cardNumber)

  return [...new Set([
    fullKey,
    fullKey.replace(/en$/, ''),
  ])].filter(Boolean)
}

/** Reconoce nombres que parecen pertenecer al escaneo de una carta. */
const looksLikeCardArtFile = (
  imageName: string
): boolean =>
  /(?:^|[\s:])(?:[A-Z0-9]+-)+[A-Z0-9]+[-_]\d+/i.test(
    imageName
  )

/** Añade el prefijo que necesita la API de ficheros de MediaWiki. */
const ensureFileTitle = (value: string): string =>
  value.startsWith('File:')
    ? value
    : `File:${value}`

/**
 * Busca la miniatura principal declarada por la página de cada carta.
 *
 * Es el camino rápido: agrupa páginas, sigue redirecciones y devuelve un
 * diccionario `{ idDeCarta: urlDeImagen }`.
 */
const fetchPrimaryImageUrls = async (
  cards: CardEntry[]
): Promise<Record<string, string>> => {
  const cardsByPageTitle = new Map<string, CardEntry[]>()
  const pageTitlesByKey = new Map<string, string>()

  /**
   * Varias entradas pueden apuntar a una misma página. Estos mapas permiten
   * pedirla una sola vez y repartir luego su imagen entre todas las cartas.
   */
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
      redirects: '1',
    })

    const cardsByResolvedTitle = new Map(
      cardsByPageTitle
    )

    const registerAlias = (
      from: string,
      to: string
    ): void => {
      /**
       * MediaWiki devuelve la página final de una redirección. Registramos ese
       * nuevo título como alias del título antiguo para no perder la relación.
       */
      const sourceCards =
        cardsByResolvedTitle.get(
          normalizePageTitleKey(from)
        ) ?? []

      if (sourceCards.length === 0) return

      const targetKey = normalizePageTitleKey(to)
      const targetCards =
        cardsByResolvedTitle.get(targetKey) ?? []

      cardsByResolvedTitle.set(
        targetKey,
        [...new Set([...targetCards, ...sourceCards])]
      )
    }

    for (const alias of json.query?.normalized ?? []) {
      registerAlias(alias.from, alias.to)
    }

    for (const redirect of json.query?.redirects ?? []) {
      registerAlias(redirect.from, redirect.to)
    }

    for (const page of json.query?.pages ?? []) {
      const imageUrl = page.thumbnail?.source

      if (!imageUrl) continue

      const matchingCards =
        cardsByResolvedTitle.get(
          normalizePageTitleKey(page.title)
        ) ?? []

      for (const card of matchingCards) {
        imageUrlsByCardId[card.id] = imageUrl
      }
    }
  }

  return imageUrlsByCardId
}

/**
 * Busca un arte japonés cuando la página no ofrece miniatura principal.
 *
 * Primero inspecciona los nombres de los ficheros de cada página; después pide
 * a MediaWiki la URL real de los ficheros seleccionados.
 */
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
        const cardNumberKeys = getCardNumberKeys(
          card.cardNumber
        )

        const selectedByNumber = imageNames.find(
          imageName => {
            const fileKey = normalizeFileKey(imageName)

            return cardNumberKeys.some(key =>
              fileKey.includes(key)
            )
          }
        )

        const cardArtFiles = imageNames.filter(
          looksLikeCardArtFile
        )

        const selectedImage =
          selectedByNumber ??
          (
            cardArtFiles.length === 1
              ? cardArtFiles[0]
              : undefined
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
  /**
   * ORQUESTACIÓN DE IMÁGENES
   * ------------------------
   * 1. Intenta miniaturas principales.
   * 2. Separa solo las cartas que siguen sin imagen.
   * 3. Aplica el fallback japonés.
   * 4. Une ambos diccionarios.
   */
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
