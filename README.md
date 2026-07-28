# VanguardTCGVault — Frontend

> El frontend se encuentra en desarrollo activo. La fuente de datos actual basada en Cardfight!! Vanguard Wiki/Fandom es temporal. La solución definitiva se apoyará en datos normalizados por el updater y una API conectada a MongoDB Atlas.

---

## Índice

- [Características actuales](#características-actuales)
- [Estado del proyecto](#estado-del-proyecto)
- [Tecnologías](#tecnologías)
- [Primeros pasos](#primeros-pasos)
- [Scripts disponibles](#scripts-disponibles)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Arquitectura actual](#arquitectura-actual)
- [Flujo de carga de cartas](#flujo-de-carga-de-cartas)
- [Búsqueda y filtros](#búsqueda-y-filtros)
- [Modelos principales](#modelos-principales)
- [Limitaciones de la fuente temporal](#limitaciones-de-la-fuente-temporal)
- [Arquitectura objetivo](#arquitectura-objetivo)
- [Contrato previsto con la API](#contrato-previsto-con-la-api)
- [Migración futura a MongoDB](#migración-futura-a-mongodb)
- [Convenciones de desarrollo](#convenciones-de-desarrollo)
- [Roadmap](#roadmap)
- [Diagramas pendientes](#diagramas-pendientes)
- [Licencia](#licencia)

---

## Características actuales

- Exploración de booster sets de Cardfight!! Vanguard.
- Carga de cartas por set.
- Carga de catálogos por generación.
- Vista en cuadrícula y vista en filas.
- Paginación de resultados.
- Carga progresiva de imágenes.
- Apertura de la ficha original de cada carta en la wiki.
- Filtros básicos por:
  - Generación.
  - Booster set.
  - Nación.
  - Grado.
- Búsqueda textual temporal mediante la wiki.
- Carga bajo demanda del efecto en inglés al usar la vista de filas.
- Caché en memoria mediante Pinia para evitar repetir peticiones dentro de la misma sesión.

---

## Estado del proyecto

### Implementado o en funcionamiento

- Consulta y listado de booster sets.
- Carga de Card Lists de boosters.
- Normalización ligera de cartas para mostrarlas en la aplicación.
- Carga de imágenes de cartas visibles.
- Navegación entre páginas de resultados.
- Vista `grid` y vista `list`.
- Visualización de efectos en inglés de cartas visibles.
- Búsqueda y filtrado básico dentro del ámbito ya cargado.

### Temporal o en revisión

La aplicación usa actualmente Fandom/MediaWiki como fuente de datos temporal.

Esto permite avanzar con la interfaz, validar la experiencia de uso y diseñar el modelo de búsqueda, pero no es una solución adecuada para filtros globales complejos.

Los filtros de:

- Clan.
- Tipo de carta.
- Trigger.
- Texto de efecto global.
- Búsquedas combinadas entre generaciones.

deben resolverse finalmente mediante consultas a una API propia, no descargando miles de fichas de Fandom desde el navegador.

---

## Tecnologías

- [Vue 3](https://vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vite.dev/)
- [Pinia](https://pinia.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- Tailwind CSS
- shadcn-vue / Reka UI
- lucide-vue-next
- Cardfight!! Vanguard Wiki / Fandom como fuente temporal de datos

---

## Primeros pasos

### Requisitos

- Node.js LTS.
- npm.
- Git.

### Instalación

Desde la raíz del repositorio:

```bash
cd vangvault
npm install
```

### Ejecutar en desarrollo

```bash
npm run dev
```

Vite mostrará una dirección local, habitualmente:

```text
http://localhost:5173
```

---

## Scripts disponibles

### Desarrollo

```bash
npm run dev
```

Inicia el servidor local de Vite con recarga automática.

### Compilación de producción

```bash
npm run build
```

Ejecuta la comprobación de tipos con TypeScript y genera la versión optimizada de producción.

### Vista previa de producción

```bash
npm run preview
```

Sirve localmente la compilación generada por `npm run build`.

---

## Estructura del proyecto

```text
vangvault/
├── public/
│   └── recursos estáticos públicos
│
├── src/
│   ├── assets/
│   │   └── imágenes y recursos internos
│   │
│   ├── components/
│   │   ├── cards/
│   │   │   ├── CardGrid.vue
│   │   │   ├── CardItem.vue
│   │   │   └── CardRow.vue
│   │   │
│   │   ├── filters/
│   │   │   ├── CardFilters.vue
│   │   │   └── card-filters.types.ts
│   │   │
│   │   └── ui/
│   │       └── componentes reutilizables de interfaz
│   │
│   ├── models/
│   │   ├── booster.model.ts
│   │   ├── card-entry.model.ts
│   │   └── card-detail.model.ts
│   │
│   ├── router/
│   │   └── definición de rutas
│   │
│   ├── services/
│   │   └── wiki/
│   │       └── wiki.client.ts
│   │
│   ├── stores/
│   │   ├── booster/
│   │   │   ├── booster.store.ts
│   │   │   └── helpers/
│   │   │
│   │   ├── card/
│   │   │   ├── card.store.ts
│   │   │   └── helpers/
│   │   │
│   │   └── filter/
│   │
│   ├── views/
│   │   ├── CardsView.vue
│   │   └── CardDetailView.vue
│   │
│   ├── App.vue
│   ├── main.ts
│   └── style.css
│
├── package.json
├── vite.config.ts
└── README.md
```

---

## Responsabilidad de cada capa

### `components/`

Contiene componentes visuales y reutilizables.

Los componentes no deben conocer detalles de scraping, HTML de Fandom, proxies ni peticiones de red complejas.

Ejemplos:

- `CardFilters.vue`: interfaz de filtros.
- `CardGrid.vue`: estructura de cuadrícula, filas y paginación.
- `CardItem.vue`: representación de una carta en cuadrícula.
- `CardRow.vue`: representación de una carta en formato detallado.

### `views/`

Orquesta la pantalla completa.

`CardsView.vue` combina:

- Filtros.
- Estado de búsqueda.
- Vista seleccionada.
- Paginación.
- Stores.
- Resultados.

A largo plazo, la vista no debe conocer si los datos vienen de Fandom, JSON, MongoDB o una API.

### `models/`

Define los contratos de datos usados por el frontend.

La aplicación diferencia entre una carta ligera de listado y una ficha detallada.

### `stores/`

Gestionan estado, caché y acciones de aplicación con Pinia.

Ejemplos:

- Booster sets cargados.
- Cartas de un set.
- Cartas agrupadas por generación.
- Imágenes resueltas.
- Detalles de cartas ya consultadas.
- Estados de carga y errores.

### `helpers/`

Contienen lógica técnica especializada.

Ejemplos:

- Obtener HTML.
- Extraer filas de una Card List.
- Mapear filas HTML a modelos internos.
- Resolver imágenes.
- Consultar una ficha individual.
- Ejecutar tareas con concurrencia limitada.

### `services/wiki/`

Centraliza la comunicación temporal con la wiki.

Debe contener toda la lógica relacionada con:

- MediaWiki.
- Fandom.
- Proxies.
- Fallbacks.
- Conversión de URL de wiki a título de página.

---

# Arquitectura actual

La arquitectura actual usa Fandom como fuente temporal.

```text
Components / Views
        ↓
Pinia Stores
        ↓
Helpers de cartas y boosters
        ↓
Wiki Client
        ↓
MediaWiki / Fandom / Proxy temporal
```

Flujo simplificado:

```text
CardsView
   ↓
CardStore
   ↓
card-list.api.ts
   ↓
wiki.client.ts
   ↓
Cardfight!! Vanguard Wiki
```

La lógica de acceso a wiki está centralizada en `wiki.client.ts` para evitar que cada componente implemente por separado proxies, URLs o fallbacks.

---

## Flujo de carga de cartas

<img width="1268" height="512" alt="2026-07-05 20_00_50-backup movil - Explorador de archivos" src="https://github.com/user-attachments/assets/64fded09-ea91-4e32-9a7e-d77ff858de50" />

### Carga de un booster concreto

```text
Usuario selecciona un set
        ↓
Pulsa Buscar
        ↓
CardStore carga la Card List del booster
        ↓
Extractor obtiene filas de la tabla
        ↓
Mapper transforma filas en CardEntry[]
        ↓
Las cartas se guardan en caché
        ↓
Se muestran resultados
        ↓
Las imágenes visibles se resuelven bajo demanda
```

### Carga de una generación

```text
Usuario selecciona una generación
        ↓
Pulsa Buscar
        ↓
CardStore identifica los boosters de esa generación
        ↓
Carga Card Lists con concurrencia limitada
        ↓
Agrupa CardEntry[] en cardsByGeneration
        ↓
Muestra resultados paginados
        ↓
Resuelve imágenes solo de cartas visibles
```

La carga por generación no debe descargar imágenes ni efectos de todas las cartas al mismo tiempo.

---

## Búsqueda y filtros

La interfaz diferencia entre dos tipos de acción.

### 1. Búsqueda que define el ámbito

Estas opciones pueden cambiar el conjunto de cartas disponible y, por tanto, requieren pulsar el botón **Buscar**:

- Booster set.
- Generación.
- Texto de búsqueda global o en efecto.

Ejemplos:

```text
Gen: DZ
Texto: Shojodoji
```

```text
Set: DZ-BT08
Texto: Stealth Rogue
```

### 2. Filtros reactivos locales

Una vez existe un conjunto de cartas cargado, estos filtros deben reaccionar sin volver a cargar todos los sets:

- Nación.
- Grado.
- Clan.
- Tipo.
- Trigger.

Actualmente, Nación y Grado pueden resolverse directamente desde los datos de Card List.

Clan, Tipo y Trigger requieren metadatos estructurados que no están disponibles de forma fiable en todas las tablas de booster de Fandom. Por este motivo, su solución definitiva dependerá de la base de datos normalizada y la API propia.

---

## Modelos principales

### `BoosterSet`

Representa un set de cartas.

```ts
export type BoosterSet = {
  name: string
  url: string

  code?: string
  generation?: string
}
```

### `CardEntry`

Representa una carta ligera dentro de una Card List.

No contiene todavía toda la información de una carta.

```ts
export type CardEntry = {
  id: string

  setKey: string
  setCode?: string
  generation?: string

  cardNumber: string
  name: string
  wikiUrl: string

  grade?: string

  nation?: string
  nationKey?: string

  listType?: string
  rarity?: string

  imageUrl?: string
}
```

Se usa para:

- Listados.
- Cuadrícula.
- Paginación.
- Filtros básicos.
- Enlace a wiki.
- Carga de imágenes.

### `CardDetail`

Representa datos que proceden de la ficha individual de una carta.

```ts
export type CardDetail = {
  cardId: string

  effectEn?: string
  effectJp?: string

  clan?: string

  cardType?: 'unit' | 'trigger' | 'order' | 'blitz'

  trigger?: 'draw' | 'critical' | 'front' | 'heal' | 'over'
}
```

Se usa para:

- Vista en fila.
- Mostrar efectos.
- Búsqueda en texto de efecto.
- Filtros avanzados.
- Futuros detalles de carta.

---

## Estrategia temporal de rendimiento

La wiki no debe convertirse en una base de datos consultada masivamente desde el navegador.

Por ello, durante la fase temporal:

- Se cargan Card Lists, no fichas completas de miles de cartas.
- Las imágenes se piden solo para cartas visibles.
- Los efectos se solicitan solo al abrir la vista de filas o una ficha concreta.
- Las peticiones simultáneas se limitan.
- Los resultados se guardan en memoria mediante Pinia.
- No se deben lanzar cientos o miles de peticiones paralelas.

Ejemplo correcto:

```text
Cargar generación DZ
→ obtener Card Lists
→ mostrar resultados
→ cargar imágenes de la página actual
→ cargar detalles solo de cartas visibles en modo fila
```

Ejemplo incorrecto:

```text
Cargar generación DZ
→ descargar todas las Card Lists
→ descargar la ficha completa de cada carta
→ descargar todas las imágenes
→ intentar filtrar después
```

---

## Limitaciones de la fuente temporal

La wiki permite avanzar durante el desarrollo, pero presenta limitaciones importantes.

### Dependencia de estructura HTML

El scraper depende de tablas y clases CSS de Fandom.

Si la wiki modifica:

- Nombres de columnas.
- Orden de filas.
- Clases CSS.
- Estructura de `Card Effect(s)`.
- Formato de imágenes.

el extractor puede dejar de funcionar.

### CORS y proxies

El navegador no siempre puede consultar directamente Fandom por políticas CORS.

Por ese motivo, el cliente temporal puede recurrir a:

- Proxy local de Vite.
- API de MediaWiki.
- AllOrigins u otros fallbacks.

### Búsquedas globales costosas

Buscar texto de efecto, clan, tipo o trigger sobre miles de cartas no debe resolverse descargando fichas individuales en el navegador.

La solución debe ser una consulta indexada en servidor.

### Paginación temporal

Durante la fase de wiki, la paginación puede operar sobre cartas ya cargadas localmente.

Cuando exista API propia, la paginación deberá ser server-side y devolver:

- Resultados de la página solicitada.
- Total real de resultados.
- Página actual.
- Tamaño de página.

---

# Arquitectura objetivo

La arquitectura final no permitirá que el navegador consulte MongoDB Atlas directamente.

El updater normalizará los datos y los almacenará en MongoDB Atlas. Una API intermedia será responsable de exponer consultas seguras y eficientes.

```text
Vue Components
        ↓
Views
        ↓
Pinia Stores
        ↓
CardRepository
        ↓
HTTP API
        ↓
MongoDB Atlas
        ↑
Updater / Scraper / Normalizador
```

La interfaz no debe saber si los datos proceden de:

- Fandom.
- Un JSON estático.
- Un endpoint serverless.
- MongoDB Atlas.
- Otra fuente futura.

Debe comunicarse únicamente con un contrato común.

---

## Repositorio de cartas previsto

La capa pendiente de introducir es un repositorio.

```ts
export interface CardRepository {
  search(
    query: CardSearchQuery
  ): Promise<CardSearchResult>

  findById(
    cardId: string
  ): Promise<CardRecord | null>

  getBoosters(
    query?: BoosterSearchQuery
  ): Promise<BoosterRecord[]>
}
```

Durante la transición existirán dos implementaciones.

```text
WikiCardRepository
→ implementación temporal basada en Fandom

ApiCardRepository
→ implementación final basada en API + MongoDB
```

El objetivo es que el store cambie de implementación sin modificar:

- `CardFilters.vue`
- `CardGrid.vue`
- `CardItem.vue`
- `CardRow.vue`
- `CardsView.vue`

---

## Contrato previsto con la API

### Consulta

```ts
export type CardSearchQuery = {
  text?: string

  generation?: string
  setCode?: string

  nation?: string
  clan?: string

  grade?: string

  type?: 'unit' | 'trigger' | 'order' | 'blitz'

  trigger?:
    | 'draw'
    | 'critical'
    | 'front'
    | 'heal'
    | 'over'

  page?: number
  pageSize?: number

  language?: 'en' | 'jp'
}
```

### Resultado paginado

```ts
export type CardSearchResult = {
  items: CardRecord[]

  total: number
  page: number
  pageSize: number
  totalPages: number
}
```

### Carta normalizada

```ts
export type CardRecord = {
  id: string

  generation: string

  setCode: string
  setName: string

  cardNumber: string

  nameEn: string
  nameJp?: string

  nation?: string
  clan?: string

  grade?: string

  cardType?: 'unit' | 'trigger' | 'order' | 'blitz'

  trigger?:
    | 'draw'
    | 'critical'
    | 'front'
    | 'heal'
    | 'over'

  rarity?: string

  effectEn?: string
  effectJp?: string

  imageEn?: string
  imageJp?: string

  wikiUrl?: string
}
```

### Ejemplo de consulta final

```text
GET /api/cards?
  text=Shojodoji&
  generation=DZ&
  clan=Murakumo&
  type=unit&
  page=1&
  pageSize=20
```

La API deberá devolver solo los resultados de la página solicitada, junto con el total real.

---

## Migración futura a MongoDB

Cuando el updater y MongoDB Atlas estén preparados, el trabajo de frontend deberá seguir este orden.

### 1. Acordar el modelo normalizado

Definir junto al updater:

- Identificador único de carta.
- Generación.
- Set.
- Número de carta.
- Nombre EN y JP.
- Nación.
- Clan.
- Grado.
- Tipo.
- Trigger.
- Rareza.
- Efecto EN y JP.
- URL de imagen EN y JP.
- URL de ficha original.

### 2. Definir la API

Acordar:

- Endpoints.
- Query params.
- Paginación.
- Filtros.
- Ordenación.
- Errores.
- Límites.
- Versionado.

### 3. Crear `CardRepository`

Crear una interfaz estable para no acoplar componentes al origen de datos.

### 4. Crear `ApiCardRepository`

Esta implementación deberá consultar la API propia.

```text
Frontend
→ fetch('/api/cards?...')
→ API
→ MongoDB Atlas
```

### 5. Adaptar `card.store.ts`

El store debe dejar de conocer:

- HTML.
- Selectores CSS.
- Tablas de Fandom.
- Proxies.
- MediaWiki.
- AllOrigins.
- Extractores de wiki.

El store solo debe conocer:

```ts
cardRepository.search(query)
```

### 6. Mantener la interfaz intacta

La migración no debe obligar a rehacer:

- Grid.
- Fila.
- Paginación.
- Filtros.
- Rutas.
- Componentes UI.

---

## Convenciones de desarrollo

### No hacer fetch desde componentes visuales

Incorrecto:

```ts
// CardRow.vue
await fetch('...')
```

Correcto:

```text
CardRow.vue
→ recibe props

CardsView.vue
→ coordina

CardStore
→ solicita datos

Repository / Service
→ realiza la petición
```

### No mezclar scraping con estado

Incorrecto:

```text
CardStore
→ querySelector()
→ parsear HTML
→ construir objetos
→ actualizar estado
```

Objetivo final:

```text
Repository
→ obtiene datos

Mapper / Adapter
→ normaliza datos

CardStore
→ mantiene estado y caché
```

### Mantener tipos estrictos

No usar:

```ts
any
```

Preferir:

```ts
CardEntry
CardDetail
CardRecord
CardSearchQuery
CardSearchResult
```

### Antes de subir cambios

```bash
npm run build
```

Comprobar también:

- Que la vista grid funciona.
- Que la vista fila funciona.
- Que la paginación no se rompe.
- Que no se han introducido peticiones masivas.
- Que los cambios no dependen de datos hardcodeados.

---

## Roadmap

### Interfaz y experiencia

- [x] Vista de cartas en cuadrícula.
- [x] Vista de cartas en filas.
- [x] Paginación.
- [x] Selector de generación.
- [x] Selector de booster set.
- [x] Filtro por nación.
- [x] Filtro por grado.
- [x] Carga progresiva de imágenes.
- [x] Enlace a la ficha de wiki.
- [x] Efecto en inglés bajo demanda.
- [ ] Selector de idioma EN / JP en filas.
- [ ] Mejoras visuales de loaders, placeholders y errores.
- [ ] Página de detalle completa.
- [ ] Ordenación de resultados.
- [ ] Filtros guardados en URL.
- [ ] Filtros favoritos o presets de búsqueda.

### Datos temporales

- [x] Cliente genérico de wiki.
- [x] Extracción de booster sets.
- [x] Extracción de Card Lists.
- [x] Resolución progresiva de imágenes.
- [x] Lectura de efectos desde `Card Effect(s)`.
- [ ] Consolidar y estabilizar extracción de metadatos de ficha.
- [ ] Revisar casos especiales de Fandom.
- [ ] Eliminar soluciones temporales que impliquen indexar miles de fichas en navegador.

### Datos definitivos

- [ ] Finalizar updater.
- [ ] Definir esquema normalizado.
- [ ] Publicar datos en MongoDB Atlas.
- [ ] Crear API de consulta.
- [ ] Crear `CardRepository`.
- [ ] Crear `ApiCardRepository`.
- [ ] Migrar `card.store.ts` a la API.
- [ ] Implementar filtros avanzados server-side.
- [ ] Implementar paginación server-side.
- [ ] Implementar búsqueda por efecto EN y JP.
- [ ] Implementar caché por query y página.



## Licencia

Consulta el archivo [`LICENSE`](../LICENSE) del repositorio principal.
