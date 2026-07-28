# VangVault

Aplicación Vue 3 + TypeScript para consultar sets y cartas de Cardfight!!
Vanguard a partir de la wiki de Fandom.

## Antes de tocar el código

Lee [docs/DATA_FLOW.md](docs/DATA_FLOW.md). Explica con nombres de fichero:

- dónde se hace cada `fetch`;
- qué HTML o JSON se descarga;
- cómo se extrae y normaliza;
- en qué store se guarda;
- qué componente lo renderiza.

Los archivos principales también contienen comentarios junto al paso que
realizan.

El selector dispone de un catálogo local de seguridad. Se muestra de inmediato
y después se completa con la wiki cuando la red responde. Por eso una caída de
Fandom no debería volver a reducirlo únicamente a `All`.

## Ejecutar

```sh
npm ci
npm run dev
```

## Comprobar producción

```sh
npm run build
```

La estructura sigue esta convención:

- `*.api.ts`: define qué se pide;
- `wiki.client.ts`: ejecuta el HTTP;
- `*.extractor.ts`: lee el HTML;
- `*.parser.ts` y `*.mapper.ts`: normalizan los datos;
- `*.store.ts`: orquesta y conserva el estado;
- `views` y `components`: conectan acciones y renderizan.
