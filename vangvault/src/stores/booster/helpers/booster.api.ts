/**
 * RESPONSABILIDAD:
 * Obtener los HTML de las páginas de productos desde la API de la wiki.
 *
 * CONTEXTO:
 * - Realiza llamadas HTTP (fetch)
 * - Gestiona fallback entre distintas fuentes (proxy / allorigins)
 * - No interpreta ni transforma los datos de producto
 *
 * ENTRADA:
 * - No recibe parámetros (endpoints fijos)
 *
 * SALIDA:
 * - Devuelve HTML de las listas y títulos JSON de la categoría
 */

import {
  fetchWikiCategoryPageTitles,
  fetchWikiPageHtmlByTitle,
} from '@/services/wiki/wiki.client'

const SET_LIST_TITLES = [
  'List_of_Cardfight!!_Vanguard_Booster_Sets',
  'List_of_Cardfight!!_Vanguard_Special_Series',
] as const

const SPECIAL_SERIES_CATEGORY =
  'Category:Special Series'

export type WikiBoosterSources = {
  htmlPages: string[]
  categoryPageTitles: string[]
}

/**
 * FETCH DEL CATÁLOGO
 * ------------------
 * Descarga en paralelo:
 * - El HTML de las dos listas históricas de productos.
 * - Los miembros JSON de la categoría que suele contener antes los SS nuevos.
 *
 * `booster.extractor.ts` convertirá ambas formas en pares `{ name, url }`.
 */
export const fetchWikiBoosterSources =
  async (): Promise<WikiBoosterSources> => {
    /**
     * `Promise.allSettled` evita que una lista caída cancele la otra.
     */
    const results = await Promise.allSettled(
      SET_LIST_TITLES.map(title =>
        fetchWikiPageHtmlByTitle(title)
      )
    )

    const htmlPages = results.flatMap(
      (result, index) => {
        if (result.status === 'fulfilled') {
          return [result.value]
        }

        console.warn(
          `No se pudo cargar la fuente ${SET_LIST_TITLES[index]}`,
          result.reason
        )

        return []
      }
    )

    /**
     * Una categoría de MediaWiki no es una página de contenido normal. Se usa
     * su API `categorymembers` en vez de intentar parsearla como HTML, que era
     * lo que producía el aviso "sin HTML parseable" de la consola.
     *
     * Esta fuente es complementaria: si falla, las dos listas y el catálogo
     * local siguen siendo válidos, por lo que no se muestra un error engañoso.
     */
    const categoryPageTitles =
      await fetchWikiCategoryPageTitles(
        SPECIAL_SERIES_CATEGORY
      ).catch(() => [])

    return {
      htmlPages,
      categoryPageTitles,
    }
  }
