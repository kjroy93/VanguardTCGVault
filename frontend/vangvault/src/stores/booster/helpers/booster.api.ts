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

const PROXIED_PATH = '/wiki-api?action=parse&page=List_of_Cardfight!!_Vanguard_Booster_Sets&prop=text&formatversion=2&format=json'
const API_TARGET = 'https://cardfight.fandom.com/api.php?action=parse&page=List_of_Cardfight!!_Vanguard_Booster_Sets&prop=text&formatversion=2&format=json'
const ALLORIGINS = (target: string) => `https://api.allorigins.win/raw?url=${encodeURIComponent(target)}`

const fetchJson = async (path: string) => {
	const res = await fetch(path)
	if (!res.ok) throw new Error(`Wiki API error: ${res.status}`)
	return res.json()
}

const trySources = async (sources: Array<() => Promise<any>>) => {
	for (const src of sources) {
		try {
			return await src()
		} catch {}
	}
	throw new Error('No se pudo obtener JSON')
}

export const fetchWikiBoosterHtml = async (): Promise<string> => {
	const json = await trySources([
		() => fetchJson(PROXIED_PATH),
		() => fetchJson(ALLORIGINS(API_TARGET))
	])

	const html = json?.parse?.text
	if (!html) throw new Error('Respuesta de la wiki sin contenido')

	return html
}