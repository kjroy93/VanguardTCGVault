import type { BoosterSourceItem } from '../helpers/booster.extractor'

type CatalogDefinition = {
  name: string
  pageTitle: string
}

const WIKI_BASE_URL = 'https://cardfight.fandom.com/wiki/'

/**
 * Convierte el título interno de una página de Fandom en una URL navegable.
 *
 * Guardamos títulos en lugar de URLs escritas a mano para que espacios,
 * apóstrofes, dos puntos y otros caracteres queden codificados correctamente.
 */
const buildWikiUrl = (pageTitle: string): string =>
  `${WIKI_BASE_URL}${encodeURIComponent(
    pageTitle.replaceAll(' ', '_')
  )}`

/**
 * CATÁLOGO LOCAL DE SEGURIDAD
 * ---------------------------
 * No sustituye a la wiki. Solo permite iniciar la aplicación cuando Fandom o
 * un proxy bloquean sus peticiones.
 *
 * Cada `name` conserva el código delante porque `booster.parser.ts` lo usa
 * para obtener la generación, el tipo de producto y el número.
 */
const CATALOG_DEFINITIONS = [
  /** Serie original. */
  { name: 'VG-BT01: Descent of the King of Knights', pageTitle: 'Booster Set 1: Descent of the King of Knights' },
  { name: 'VG-BT02: Onslaught of Dragon Souls', pageTitle: 'Booster Set 2: Onslaught of Dragon Souls' },
  { name: 'VG-BT03: Demonic Lord Invasion', pageTitle: 'Booster Set 3: Demonic Lord Invasion' },
  { name: 'VG-BT04: Eclipse of Illusionary Shadows', pageTitle: 'Booster Set 4: Eclipse of Illusionary Shadows' },
  { name: 'VG-BT05: Awakening of Twin Blades', pageTitle: 'Booster Set 5: Awakening of Twin Blades' },
  { name: 'VG-BT06: Breaker of Limits', pageTitle: 'Booster Set 6: Breaker of Limits' },
  { name: 'VG-BT07: Rampage of the Beast King', pageTitle: 'Booster Set 7: Rampage of the Beast King' },
  { name: 'VG-BT08: Blue Storm Armada', pageTitle: 'Booster Set 8: Blue Storm Armada' },
  { name: 'VG-BT09: Clash of the Knights & Dragons', pageTitle: 'Booster Set 9: Clash of the Knights & Dragons' },
  { name: 'VG-BT10: Triumphant Return of the King of Knights', pageTitle: 'Booster Set 10: Triumphant Return of the King of Knights' },
  { name: 'VG-BT11: Seal Dragons Unleashed', pageTitle: 'Booster Set 11: Seal Dragons Unleashed' },
  { name: 'VG-BT12: Binding Force of the Black Rings', pageTitle: 'Booster Set 12: Binding Force of the Black Rings' },
  { name: 'VG-BT13: Catastrophic Outbreak', pageTitle: 'Booster Set 13: Catastrophic Outbreak' },
  { name: 'VG-BT14: Brilliant Strike', pageTitle: 'Booster Set 14: Brilliant Strike' },
  { name: 'VG-BT15: Infinite Rebirth', pageTitle: 'Booster Set 15: Infinite Rebirth' },
  { name: 'VG-BT16: Legion of Dragons & Blades', pageTitle: 'Booster Set 16: Legion of Dragons & Blades' },
  { name: 'VG-BT17: Blazing Perdition', pageTitle: 'Booster Set 17: Blazing Perdition' },

  /** Generación G. */
  { name: 'VG-G-BT01: Generation Stride', pageTitle: 'G Booster Set 1: Generation Stride' },
  { name: 'VG-G-BT02: Soaring Ascent of Gale & Blossom', pageTitle: 'G Booster Set 2: Soaring Ascent of Gale & Blossom' },
  { name: 'VG-G-BT03: Sovereign Star Dragon', pageTitle: 'G Booster Set 3: Sovereign Star Dragon' },
  { name: 'VG-G-BT04: Soul Strike Against the Supreme', pageTitle: 'G Booster Set 4: Soul Strike Against the Supreme' },
  { name: 'VG-G-BT05: Moonlit Dragonfang', pageTitle: 'G Booster Set 5: Moonlit Dragonfang' },
  { name: 'VG-G-BT06: Transcension of Blade & Blossom', pageTitle: 'G Booster Set 6: Transcension of Blade & Blossom' },
  { name: 'VG-G-BT07: Glorious Bravery of Radiant Sword', pageTitle: 'G Booster Set 7: Glorious Bravery of Radiant Sword' },
  { name: 'VG-G-BT08: Absolute Judgment', pageTitle: 'G Booster Set 8: Absolute Judgment' },
  { name: 'VG-G-BT09: Divine Dragon Caper', pageTitle: 'G Booster Set 9: Divine Dragon Caper' },
  { name: 'VG-G-BT10: Raging Clash of the Blade Fangs', pageTitle: 'G Booster Set 10: Raging Clash of the Blade Fangs' },
  { name: 'VG-G-BT11: Demonic Advent', pageTitle: 'G Booster Set 11: Demonic Advent' },
  { name: "VG-G-BT12: Dragon King's Awakening", pageTitle: "G Booster Set 12: Dragon King's Awakening" },
  { name: 'VG-G-BT13: Ultimate Stride', pageTitle: 'G Booster Set 13: Ultimate Stride' },
  { name: 'VG-G-BT14: Divine Dragon Apocrypha', pageTitle: 'G Booster Set 14: Divine Dragon Apocrypha' },

  /** Generación V. */
  { name: 'VG-V-BT01: Unite! Team Q4', pageTitle: 'V Booster Set 01: Unite! Team Q4' },
  { name: 'VG-V-BT02: Strongest! Team AL4', pageTitle: 'V Booster Set 02: Strongest! Team AL4' },
  { name: 'VG-V-BT03: Miyaji Academy Cardfight Club', pageTitle: 'V Booster Set 03: Miyaji Academy Cardfight Club' },
  { name: 'VG-V-BT04: Vilest! Deletor', pageTitle: 'V Booster Set 04: Vilest! Deletor' },
  { name: 'VG-V-BT05: Aerial Steed Liberation', pageTitle: 'V Booster Set 05: Aerial Steed Liberation' },
  { name: 'VG-V-BT06: Phantasmal Steed Restoration', pageTitle: 'V Booster Set 06: Phantasmal Steed Restoration' },
  { name: 'VG-V-BT07: Infinideity Cradle', pageTitle: 'V Booster Set 07: Infinideity Cradle' },
  { name: 'VG-V-BT08: Silverdust Blaze', pageTitle: 'V Booster Set 08: Silverdust Blaze' },
  { name: "VG-V-BT09: Butterfly d'Moonlight", pageTitle: "V Booster Set 09: Butterfly d'Moonlight" },
  { name: 'VG-V-BT10: Phantom Dragon Aeon', pageTitle: 'V Booster Set 10: Phantom Dragon Aeon' },
  { name: 'VG-V-BT11: Storm of the Blue Cavalry', pageTitle: 'V Booster Set 11: Storm of the Blue Cavalry' },
  { name: 'VG-V-BT12: Divine Lightning Radiance', pageTitle: 'V Booster Set 12: Divine Lightning Radiance' },

  /** Generación D. */
  { name: 'VG-D-BT01: Genesis of the Five Greats', pageTitle: 'D Booster Set 01: Genesis of the Five Greats' },
  { name: 'VG-D-BT02: A Brush with the Legends', pageTitle: 'D Booster Set 02: A Brush with the Legends' },
  { name: 'VG-D-BT03: Advance of Intertwined Stars', pageTitle: 'D Booster Set 03: Advance of Intertwined Stars' },
  { name: 'VG-D-BT04: Awakening of Chakrabarthi', pageTitle: 'D Booster Set 04: Awakening of Chakrabarthi' },
  { name: 'VG-D-BT05: Triumphant Return of the Brave Heroes', pageTitle: 'D Booster Set 05: Triumphant Return of the Brave Heroes' },
  { name: 'VG-D-BT06: Blazing Dragon Reborn', pageTitle: 'D Booster Set 06: Blazing Dragon Reborn' },
  { name: 'VG-D-BT07: Raging Flames Against Emerald Storm', pageTitle: 'D Booster Set 07: Raging Flames Against Emerald Storm' },
  { name: 'VG-D-BT08: Minerva Rising', pageTitle: 'D Booster Set 08: Minerva Rising' },
  { name: 'VG-D-BT09: Dragontree Invasion', pageTitle: 'D Booster Set 09: Dragontree Invasion' },
  { name: 'VG-D-BT10: Dragon Masquerade', pageTitle: 'D Booster Set 10: Dragon Masquerade' },
  { name: 'VG-D-BT11: Clash of the Heroes', pageTitle: 'D Booster Set 11: Clash of the Heroes' },
  { name: 'VG-D-BT12: Evenfall Onslaught', pageTitle: 'D Booster Set 12: Evenfall Onslaught' },
  { name: 'VG-D-BT13: Flight of Chakrabarthi', pageTitle: 'D Booster Set 13: Flight of Chakrabarthi' },

  /** Generación DZ. */
  { name: 'VG-DZ-BT01: Fated Clash', pageTitle: 'DZ Booster Set 01: Fated Clash' },
  { name: 'VG-DZ-BT02: Illusionless Strife', pageTitle: 'DZ Booster Set 02: Illusionless Strife' },
  { name: 'VG-DZ-BT03: Dimensional Transcendence', pageTitle: 'DZ Booster Set 03: Dimensional Transcendence' },
  { name: 'VG-DZ-BT04: Destined Showdown', pageTitle: 'DZ Booster Set 04: Destined Showdown' },
  { name: 'VG-DZ-BT05: Omniscient Awakening', pageTitle: 'DZ Booster Set 05: Omniscient Awakening' },
  { name: 'VG-DZ-BT06: Generation Dragenesis', pageTitle: 'DZ Booster Set 06: Generation Dragenesis' },
  { name: 'VG-DZ-BT07: Moon Fangs & Cerulean Blaze', pageTitle: 'DZ Booster Set 07: Moon Fangs & Cerulean Blaze' },
  { name: 'VG-DZ-BT08: Knights 0f Rebirth', pageTitle: 'DZ Booster Set 08: Knights 0f Rebirth' },
  { name: 'VG-DZ-BT09: Super Brave Detonation', pageTitle: 'DZ Booster Set 09: Super Brave Detonation' },
  { name: 'VG-DZ-BT10: Dragonsoul Resonance', pageTitle: 'DZ Booster Set 10: Dragonsoul Resonance' },
  { name: 'VG-DZ-BT11: Symphony of Might & Bloom', pageTitle: 'DZ Booster Set 11: Symphony of Might & Bloom' },
  { name: 'VG-DZ-BT12: Chasm of Lost Souls', pageTitle: 'DZ Booster Set 12: Chasm of Lost Souls' },
  { name: 'VG-DZ-BT13: Parallactic Clash', pageTitle: 'DZ Booster Set 13: Parallactic Clash' },
  { name: 'VG-DZ-BT14: Envoys of the Crimson Moon', pageTitle: 'DZ Booster Set 14: Envoys of the Crimson Moon' },
  { name: 'VG-DZ-BT15: Strike of Illusionary Shadows', pageTitle: 'DZ Booster Set 15: Strike of Illusionary Shadows' },
  { name: 'VG-DZ-BT16: Parallactic Dawn', pageTitle: 'DZ Booster Set 16: Parallactic Dawn' },

  /** Special Series D. */
  { name: 'VG-D-SS01: Festival Collection 2021', pageTitle: 'D Special Series 01: Festival Collection 2021' },
  { name: 'VG-D-SS02: Festival Collection 2022', pageTitle: 'D Special Series 02: Festival Collection 2022' },
  { name: 'VG-D-SS03: Stride Deckset Chronojet', pageTitle: 'D Special Series 03: Stride Deckset Chronojet' },
  { name: 'VG-D-SS04: Stride Deckset Messiah', pageTitle: 'D Special Series 04: Stride Deckset Messiah' },
  { name: 'VG-D-SS05: Festival Booster 2023', pageTitle: 'D Special Series 05: Festival Booster 2023' },
  { name: 'VG-D-SS06: Stand Up Deckset “Gramgrace”', pageTitle: 'D Special Series 06: Stand Up Deckset "Gramgrace"' },
  { name: 'VG-D-SS07: Stand Up Deckset “Favrneel”', pageTitle: 'D Special Series 07: Stand Up Deckset "Favrneel"' },
  { name: 'VG-D-SS08: Stand Up Deckset “Orfist”', pageTitle: 'D Special Series 08: Stand Up Deckset "Orfist"' },
  { name: 'VG-D-SS09: Stride Deckset Shiranui', pageTitle: 'D Special Series 09: Stride Deckset Shiranui' },
  { name: 'VG-D-SS10: Stride Deckset Luard', pageTitle: 'D Special Series 10: Stride Deckset Luard' },
  { name: 'VG-D-SS11: Triple Drive Booster', pageTitle: 'D Special Series 11: Triple Drive Booster' },

  /** Special Series DZ. */
  { name: 'VG-DZ-SS01: Festival Booster 2024', pageTitle: 'DZ Special Series 01: Festival Booster 2024' },
  { name: 'VG-DZ-SS02: Stride Deckset Harri', pageTitle: 'DZ Special Series 02: Stride Deckset Harri' },
  { name: 'VG-DZ-SS03: Stride Deckset Nightrose', pageTitle: 'DZ Special Series 03: Stride Deckset Nightrose' },
  { name: 'VGE-DZ-SS04: CoroCoro Start Deck Pack', pageTitle: 'DZ Special Series 04: CoroCoro Start Deck Pack' },
  { name: 'VGE-DZ-SS04: Stardust Blade', pageTitle: 'DZ Special Series 04: Stardust Blade' },
  { name: "VG-DZ-SS05: Fighter's Coin Set -Fated Clash-", pageTitle: "DZ Special Series 05: Fighter's Coin Set -Fated Clash-" },
  { name: "VG-DZ-SS06: Fighter's Coin Set -Destined Showdown-", pageTitle: "DZ Special Series 06: Fighter's Coin Set -Destined Showdown-" },
  { name: 'VG-DZ-SS07: Break Away Start Deck - Battle with “Power”! Zero Tendo', pageTitle: 'DZ Special Series 07: Break Away Start Deck - Battle with "Power"! Zero Tendo' },
  { name: 'VG-DZ-SS08: Break Away Start Deck - Battle with “Skill”! Shiki Otei', pageTitle: 'DZ Special Series 08: Break Away Start Deck - Battle with "Skill"! Shiki Otei' },
  { name: 'VG-DZ-SS09: Master Deckset -Urara Haneyama-', pageTitle: 'DZ Special Series 09: Master Deckset -Urara Haneyama-' },
  { name: 'VG-DZ-SS10: Master Deckset -Michiru Hazama-', pageTitle: 'DZ Special Series 10: Master Deckset -Michiru Hazama-' },
  { name: 'VGE-DZ-SS11: Festival Booster 2025', pageTitle: 'DZ Special Series 11: Festival Booster 2025' },
  { name: 'DZ Special Series 12: Master Deckset -Hikari Myodo-', pageTitle: 'DZ Special Series 12: Master Deckset -Hikari Myodo-' },
  { name: 'DZ Special Series 13: Master Deckset -Erika Myojo-', pageTitle: 'DZ Special Series 13: Master Deckset -Erika Myojo-' },
  { name: 'DZ Special Series 14: Break Away Start Deck - Blaster Blade', pageTitle: 'DZ Special Series 14: Break Away Start Deck - Blaster Blade' },
  { name: 'DZ Special Series 15: Break Away Start Deck - Dragonic Overlord', pageTitle: 'DZ Special Series 15: Break Away Start Deck - Dragonic Overlord' },
  { name: 'DZ Special Series 16: The Legendary Vanguards', pageTitle: 'DZ Special Series 16: The Legendary Vanguards' },
] satisfies CatalogDefinition[]

/**
 * Forma final que entiende `booster.store.ts`.
 *
 * La conversión se hace una sola vez al importar el módulo.
 */
export const FALLBACK_BOOSTER_ITEMS: BoosterSourceItem[] =
  CATALOG_DEFINITIONS.map(definition => ({
    name: definition.name,
    url: buildWikiUrl(definition.pageTitle),
  }))
