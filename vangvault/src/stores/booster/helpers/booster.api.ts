/**
 * RESPONSABILIDAD:
 * Obtener los HTML de las páginas de productos desde la API de la wiki.
 *
 * CONTEXTO:
 * - Realiza llamadas HTTP (fetch)
 * - Gestiona fallback entre distintas fuentes (proxy / allorigins)
 * - No interpreta ni transforma los datos
 *
 * ENTRADA:
 * - No recibe parámetros (endpoints fijos)
 *
 * SALIDA:
 * - Devuelve los HTML de Booster Sets, Special Series y su categoría
 */

import { fetchWikiPageHtmlByTitle } from '@/services/wiki/wiki.client'

const SET_LIST_TITLES = [
  'List_of_Cardfight!!_Vanguard_Booster_Sets',
  'List_of_Cardfight!!_Vanguard_Special_Series',
  /**
   * La lista histórica puede tardar en actualizarse. La categoría sí incluye
   * los SS nuevos, por ejemplo DZ-SS12 ... DZ-SS16.
   */
  'Category:Special_Series',
] as const

/**
 * FETCH DEL CATÁLOGO
 * ------------------
 * Descarga en paralelo las tres páginas que describen los productos.
 * La salida sigue siendo HTML crudo; `booster.extractor.ts` lo convierte
 * después en pares `{ name, url }`.
 */
export const fetchWikiBoosterHtmlPages =
  async (): Promise<string[]> => {
    /**
     * `Promise.allSettled` espera todas las fuentes sin cancelar el conjunto
     * cuando falla una. Con `Promise.all`, un error de la categoría provocaba
     * que se perdieran también las otras páginas que sí habían respondido.
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

    return htmlPages
  }
