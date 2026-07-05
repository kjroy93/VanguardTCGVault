/**
 * RESPONSABILIDAD:
 * Obtener el HTML de la página de boosters desde la API de la wiki.
 *
 * CONTEXTO:
 * - Realiza llamadas HTTP (fetch)
 * - Gestiona fallback entre distintas fuentes (proxy / allorigins)
 * - No interpreta ni transforma los datos
 *
 * ENTRADA:
 * - No recibe parámetros (endpoint fijo)
 *
 * SALIDA:
 * - Devuelve el HTML como string
 */

import { fetchWikiPageHtmlByTitle } from '@/services/wiki/wiki.client'

const BOOSTER_LIST_TITLE =
  'List_of_Cardfight!!_Vanguard_Booster_Sets'

export const fetchWikiBoosterHtml = (): Promise<string> =>
  fetchWikiPageHtmlByTitle(BOOSTER_LIST_TITLE)