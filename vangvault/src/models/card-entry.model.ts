export type CardKind =
  | 'unit'
  | 'trigger'
  | 'order'
  | 'blitz'

export type TriggerKind =
  | 'draw'
  | 'critical'
  | 'front'
  | 'heal'
  | 'over'
  | 'stand'

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

  /**
   * Texto original recibido en la columna `Type` de la Card List.
   * Se conserva para depurar cambios de formato en la wiki.
   */
  listType?: string

  /**
   * Campos categóricos derivados de `listType`.
   *
   * La interfaz filtra con estas claves exactas, no buscando palabras en el
   * efecto. El updater y una futura base de datos deberán producir las mismas
   * claves para poder cambiar de fuente sin cambiar la vista.
   */
  cardKind?: CardKind
  triggerKind?: TriggerKind

  rarity?: string

  /**
   * Se rellenará en la fase de imágenes.
   */
  imageUrl?: string
}
