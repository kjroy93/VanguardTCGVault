export type CardEntry = {
  /**
   * Identificador interno seguro y único dentro de la aplicación.
   * Aún no se usa como parámetro de ruta.
   */
  id: string

  /**
   * Identifica el set que cargó esta carta.
   * Usamos la URL del booster como clave de caché.
   */
  setKey: string

  setCode?: string
  generation?: string

  /**
   * Ejemplo: D-LBT04/011
   */
  cardNumber: string

  name: string
  wikiUrl: string

  grade?: string
  nation?: string
  nationKey?: string
  listType?: string
  rarity?: string

  /**
   * Se rellenará en la fase de imágenes.
   */
  imageUrl?: string
}