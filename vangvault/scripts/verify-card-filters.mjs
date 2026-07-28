import assert from 'node:assert/strict'
import { createServer } from 'vite'

/**
 * Carga los módulos TypeScript con Vite para probar exactamente el código que
 * ejecutará la aplicación, incluidos sus alias `@/`.
 */
const server = await createServer({
  appType: 'custom',
  logLevel: 'silent',
  server: {
    middlewareMode: true,
  },
})

try {
  const {
    mapCardListRowsToEntries,
  } = await server.ssrLoadModule(
    '/src/stores/card/helpers/card-list.mapper.ts'
  )

  const {
    cardQuerySource,
  } = await server.ssrLoadModule(
    '/src/stores/card/data/card-query.source.ts'
  )

  const booster = {
    name: 'Filter fixture',
    url: 'https://cardfight.fandom.com/wiki/Filter_fixture',
    code: 'TEST-SS01',
    generation: 'DZ',
  }

  const cards = mapCardListRowsToEntries([
    {
      cardNumber: 'TEST/001',
      name: 'Normal Grade One',
      wikiUrl:
        'https://cardfight.fandom.com/wiki/Normal_Grade_One',
      grade: '1',
      listType: 'Normal',
    },
    {
      cardNumber: 'TEST/002',
      name: 'Exact Critical',
      wikiUrl:
        'https://cardfight.fandom.com/wiki/Exact_Critical',
      grade: '0',
      listType: 'Critical',
    },
    {
      cardNumber: 'TEST/003',
      name: 'Exact Heal',
      wikiUrl:
        'https://cardfight.fandom.com/wiki/Exact_Heal',
      grade: '0',
      listType: 'Heal Trigger',
    },
  ], booster)

  /**
   * Critical debe resolverse con el metadato normalizado, sin consultar la red
   * y sin incluir una Normal Unit aunque su ficha pudiera mencionar triggers.
   */
  globalThis.fetch = async () => {
    throw new Error(
      'Critical no debería necesitar un fetch'
    )
  }

  const criticalResult =
    await cardQuerySource.searchMetadata(cards, {
      clan: 'all',
      type: 'all',
      trigger: 'critical',
    })

  assert.deepEqual(
    [...criticalResult.cardIds],
    [cards[1].id]
  )

  const triggerTypeResult =
    await cardQuerySource.searchMetadata(cards, {
      clan: 'all',
      type: 'trigger',
      trigger: 'all',
    })

  assert.deepEqual(
    [...triggerTypeResult.cardIds],
    [cards[1].id, cards[2].id]
  )

  const unitTypeResult =
    await cardQuerySource.searchMetadata(cards, {
      clan: 'all',
      type: 'unit',
      trigger: 'all',
    })

  assert.deepEqual(
    [...unitTypeResult.cardIds],
    [cards[0].id]
  )

  /**
   * Clan todavía usa MediaWiki. Se comprueba que la consulta usa una categoría
   * exacta y que su resultado se intersecta con Critical.
   */
  let clanQuery = ''

  globalThis.fetch = async input => {
    const url = new URL(String(input))
    clanQuery = url.searchParams.get('srsearch') ?? ''

    return new Response(JSON.stringify({
      query: {
        search: [
          { title: 'Exact Critical' },
          { title: 'Normal Grade One' },
        ],
      },
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  const intersectionResult =
    await cardQuerySource.searchMetadata(cards, {
      clan: 'Kagero',
      type: 'trigger',
      trigger: 'critical',
    })

  assert.equal(
    clanQuery,
    'incategory:"Kagero"'
  )

  assert.deepEqual(
    [...intersectionResult.cardIds],
    [cards[1].id]
  )

  /**
   * La categoría de Special Series debe viajar por `categorymembers`, no por
   * el parser HTML que producía el aviso amarillo.
   */
  const {
    fetchWikiBoosterSources,
  } = await server.ssrLoadModule(
    '/src/stores/booster/helpers/booster.api.ts'
  )

  const {
    extractBoostersFromTitles,
  } = await server.ssrLoadModule(
    '/src/stores/booster/helpers/booster.extractor.ts'
  )

  const requestedActions = []

  globalThis.fetch = async input => {
    const url = new URL(String(input))
    const action = url.searchParams.get('action')
    const list = url.searchParams.get('list')

    requestedActions.push(
      list ? `${action}:${list}` : action
    )

    if (list === 'categorymembers') {
      return new Response(JSON.stringify({
        query: {
          categorymembers: [{
            title:
              'DZ Special Series 16: The Legendary Vanguards',
          }],
        },
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
      })
    }

    return new Response(JSON.stringify({
      parse: {
        text: '<div class="mw-parser-output"></div>',
      },
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  const boosterSources =
    await fetchWikiBoosterSources()

  assert.deepEqual(
    requestedActions.sort(),
    [
      'parse',
      'parse',
      'query:categorymembers',
    ].sort()
  )

  const categoryBoosters = extractBoostersFromTitles(
    boosterSources.categoryPageTitles
  )

  assert.equal(categoryBoosters.length, 1)
  assert.equal(
    categoryBoosters[0].name,
    'DZ Special Series 16: The Legendary Vanguards'
  )

  console.log(
    'OK: filtros exactos y categoría Special Series por JSON.'
  )
} finally {
  await server.close()
}
