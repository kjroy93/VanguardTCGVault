# Flujo de datos de VangVault

Este documento responde, en orden, a las preguntas: dónde se hace el fetch,
qué se descarga, cómo se normaliza, dónde se guarda y dónde se renderiza.

## 1. Catálogo de sets

1. `src/views/CardsView.vue` se monta y llama a
   `boosterStore.loadFromApi()`.
2. `src/stores/booster/booster.store.ts` publica primero
   `booster-catalog.fallback.ts`, para que el selector nunca dependa por completo
   de que Fandom esté disponible.
3. `src/stores/booster/helpers/booster.api.ts` intenta actualizar ese catálogo
   mediante tres páginas índice: booster sets, special series y la categoría
   actual de special series. Si una falla, conserva las demás.
4. `src/services/wiki/wiki.client.ts` ejecuta el `fetch` HTTP por varias rutas y
   devuelve HTML. Cada intento tiene un límite de tiempo.
5. `src/stores/booster/helpers/booster.extractor.ts` convierte ese HTML en
   pares `{ name, url }`, filtra enlaces que no son productos y quita
   duplicados.
6. `src/stores/booster/helpers/booster.parser.ts` convierte cada par en
   `BoosterSet`: código, generación, número, nombre limpio y URL.
7. `src/stores/booster/booster.store.ts` mezcla la actualización con el
   respaldo y guarda los sets en `sets`.
8. `src/components/filters/CardFilters.vue` recibe `sets` como prop, los
   filtra, ordena y renderiza en el selector.

Resumen:

`CardsView -> respaldo local -> booster.api -> wiki.client -> extractor -> parser -> store -> CardFilters`

## 2. Cartas de un set

1. El usuario elige un set y pulsa **Buscar** en `CardFilters.vue`.
2. El componente emite el evento `search`.
3. `CardsView.vue`, en `handleSearch`, localiza el `BoosterSet` y llama a
   `cardStore.loadCardsFromBooster(booster)`.
4. `src/stores/card/helpers/card-list.api.ts` usa la URL del set para pedir su
   HTML mediante `wiki.client.ts`.
5. `src/stores/card/helpers/card-list.extractor.ts` encuentra la tabla
   **Card List** y la convierte en filas simples.
6. `src/stores/card/helpers/card-list.mapper.ts` transforma esas filas en
   objetos `CardEntry`.
7. `src/stores/card/card.store.ts` guarda el resultado en
   `cardsBySet[booster.url]`.
8. `CardsView.vue` lee `selectedCards`, aplica los filtros y pasa el resultado
   a `src/components/cards/CardGrid.vue`.
9. `CardGrid.vue` pagina las cartas y renderiza `CardItem.vue` o `CardRow.vue`.

Resumen:

`CardFilters -> CardsView.handleSearch -> card.store -> card-list.api -> wiki.client -> extractor -> mapper -> store -> CardGrid`

## 3. Imágenes

1. Cuando ya existen cartas, `card.store.ts` llama a
   `src/stores/card/helpers/card-image.api.ts`.
2. Primero se pide la miniatura principal de cada página de carta.
3. La petición sigue redirecciones de nombres antiguos.
4. Si no existe miniatura inglesa, se inspeccionan los ficheros de la página y
   se intenta encontrar el arte japonés por número de carta.
5. El store copia cada URL encontrada en `CardEntry.imageUrl`.
6. Como Pinia y Vue son reactivos, `CardItem.vue` se vuelve a renderizar sin
   recargar la página.

## Regla práctica para navegar el proyecto

| Sufijo o ubicación | Responsabilidad |
| --- | --- |
| `*.api.ts` | Decide qué dato externo pedir. |
| `services/wiki/wiki.client.ts` | Ejecuta el `fetch` HTTP genérico. |
| `*.extractor.ts` | Extrae estructura desde HTML crudo. |
| `*.parser.ts` / `*.mapper.ts` | Normaliza datos al modelo de la app. |
| `*.store.ts` | Orquesta pasos, mantiene estado y caché. |
| `booster-catalog.fallback.ts` | Mantiene operativo el selector si falla la red. |
| `views/*.vue` | Conecta acciones del usuario con los stores. |
| `components/*.vue` | Renderiza props y emite eventos. |

Si la wiki cambia su HTML, el primer lugar que hay que revisar es el extractor.
Si cambia un endpoint, el cliente o el archivo `*.api.ts`. Si el dato existe
pero se ve mal, hay que revisar el componente Vue que lo renderiza.
