# Evolución prevista de la fuente de datos

El objetivo futuro es que el updater alimente periódicamente un índice y que la
aplicación consulte ese índice, sin recorrer por scraping todos los sets de una
generación cada vez que alguien combina filtros.

Este documento separa lo que ya está normalizado de lo que todavía falta. No
implementa Mongo ni da por terminado el updater.

## Lo que ya queda preparado

### 1. Modelo común de carta

`src/models/card-entry.model.ts` contiene las claves que consume la interfaz:

| Campo | Ejemplo | Uso |
| --- | --- | --- |
| `id` | `vg-dz-ss16-dz-ss16-001` | Identidad estable en cachés y Vue. |
| `setKey`, `setCode`, `generation` | URL, `DZ-SS16`, `DZ` | Acotar búsquedas. |
| `cardNumber`, `name` | `DZ-SS16/001`, nombre | Identificación y texto. |
| `grade`, `nationKey` | `0`, `dragon_empire` | Filtros básicos. |
| `cardKind` | `unit`, `trigger`, `order`, `blitz` | Tipo categórico. |
| `triggerKind` | `critical`, `heal`, etc. | Trigger categórico exacto. |
| `rarity`, `wikiUrl`, `imageUrl` | valores visibles | Renderizado. |

El updater debería guardar esos conceptos normalizados aunque sus nombres de
campo en Mongo sean distintos.

### 2. Contrato de consultas

`src/stores/card/data/card-query.types.ts` define `CardQuerySource`.
`CardsView.vue` usa `cardQuerySource` y no llama directamente al buscador de
MediaWiki.

La implementación actual:

- filtra Type y Trigger con datos de la Card List;
- consulta Clan como categoría exacta de MediaWiki;
- usa el buscador de MediaWiki para texto libre.

Esto evita falsos positivos y crea una primera frontera sustituible.

## Lo que habrá que sustituir cuando el updater esté listo

Hay dos responsabilidades distintas:

1. **Cargar el ámbito**: hoy `card.store.ts` obtiene uno o varios Card Lists por
   scraping.
2. **Consultar el ámbito**: hoy `card-query.source.ts` refina las cartas ya
   cargadas.

Cambiar únicamente la segunda no evita descargar una generación completa. El
paso futuro correcto será crear un origen HTTP que reciba ámbito, filtros y
paginación en una sola petición, y que la base de datos haga allí la
intersección.

Una petición normalizada podría expresar:

```ts
type IndexedCardQuery = {
  setCode?: string
  generation?: string
  text?: string
  grade?: string
  nationKey?: string
  clans?: string[]
  cardKind?: string
  triggerKind?: string
  page: number
  pageSize: number
}
```

Su respuesta debería traer las cartas de esa página y el total, no solo ids:

```ts
type IndexedCardResult = {
  cards: CardEntry[]
  total: number
}
```

En ese momento, la acción de búsqueda de `CardsView.vue` deberá delegarse en un
servicio que elija entre:

- `wikiCardSource`: implementación actual durante la transición;
- `indexedCardSource`: llamada HTTP al índice alimentado por el updater.

## Límite de seguridad

El frontend publicado no debe contener credenciales de Mongo Atlas ni abrir una
conexión administrativa directa a la base. El updater puede escribir con sus
credenciales privadas cuando se ejecute manualmente; el navegador debería leer
mediante un endpoint HTTP con permisos y campos limitados.

Ese endpoint no exige necesariamente mantener un servidor tradicional siempre
encendido: la decisión entre una función bajo demanda y un catálogo estático
precalculado puede tomarse cuando el updater y el volumen real estén medidos.

## Índices que probablemente harán falta

La forma exacta depende de las consultas reales, pero conviene medir al menos
combinaciones que empiecen por el ámbito y continúen por los filtros más usados:

- `setCode + cardKind + triggerKind`;
- `generation + nationKey + grade`;
- `generation + clans + cardKind`;
- índice de texto para nombre, número y efecto, si el proveedor elegido lo
  permite con el plan disponible.

No hace falta crear todos por adelantado: los índices también ocupan espacio y
encarecen las escrituras del updater.
