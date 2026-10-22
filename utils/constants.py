# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    constants.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/13 11:54:05 by marvin            #+#    #+#              #
#    Updated: 2026/10/18 03:57:27 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from pathlib		import Path

# Library
from routine.fsm	import PipelineEvent

CATEGORIES = {
	"boosters": [
		"Booster Sets",
		"Extra Booster Sets",
		"Character Booster Sets",
		"Clan Booster Sets",
		"Title Booster Sets",
		"Unique Booster Sets",
	],
	"specials": [
		"Fighters Collections",
		"Revival Collections",
		"Collector's Sets",
		"Special Series"
	],
	"decks": [
		"Trial Decks",
		"Legend Decks",
		"Character Decks",
		"Half Decks",
		"Premiun Fighter Decks",
		"Structure Decks"
	],
	"others": [
		"Promo Cards",
		"V Promo Cards",
		"Monthly Bushiroad Cards"
	],
	"cards": []
}

NATIONS = {
	"Dragon Empire",
	"Dark States",
	"Brandt Gate",
	"Stoicheia",
	"Keter Sanctuary",
	"Lyrical Monasterio",
	"VSPO!",
	"CoroCoro"
}


DICT_S = {
	"boosters": [
		"List",
		"Unique",
		"G Booster Set 5: Ombre Assassine",
		"G Booster Set 6: Tempesta di Fiori",
		"G Booster Set 4: La Debolezza è un Peccato",
		"Thailand Booster Set 1: The Mask Collection",
		"G Booster Set 1: Trascendenza Interdimensionale",
		"G Booster Set 7: Giudizio delle Lame Splendenti",
		"G Booster Set 8: Collezione del Combattente Vol.1",
		"G Booster Set 9: Collezione del Combattente Vol.2",
		"G Booster Set 3: Potere Supremo del Drago Stellare",
		"G Booster Set 2: Assalto Fulmineo delle Fiamme Roventi",
	],
	"specials": [
		"List",
		"Thailand",
	],
	"decks": [
		"List",
		"Thailand"
	]
}

SET_PATHS = {
	"boosters": {
		"booster": {
			"folder": "boosters/booster sets"
		},
		"extra": {
			"folder": "boosters/extra booster sets"
		},
		"character": {
			"folder": "boosters/character booster sets"
		},
		"clan": {
			"folder": "boosters/clan booster sets"
		},
		"title": {
			"folder": "boosters/title booster sets"
		},
		"unique": {
			"folder": "boosters/unique booster sets"
		}
	},
	"decks": {
		"trial": {
			"folder": "decks/trial decks",
			"prefix": "deck"
		},
		"legend": {
			"folder": "decks/legend decks",
			"prefix": "deck"
		},
		"start": {
			"folder": "decks/start decks",
			"prefix": "deck"
		},
		"character": {
			"folder": "decks/character decks",
			"prefix": "deck"
		},
		"structure": {
			"folder": "decks/structure decks",
			"prefix": "deck"
		}
	},
	"specials": {
		"fighters": {
			"folder": "specials/fighters collections",
			"prefix": "specials"
		},
		"revival": {
			"folder": "specials/revival collections",
			"prefix": "specials"
		},
		"collector's": {
			"folder": "specials/collector's sets",
			"prefix": "specials"
		},
		"special": {
			"folder": "specials/special series",
			"prefix": "specials"
		}
	},
	"other": {
		"main": {
			"folder": "other",
			"prefix": "other"
		}
	}
}

DB_FOLDER = Path("database")
FAILURE_FILE = path = Path("database/failed_sets.json")
VALID_DATABASES = ["LB", "LL", "G", "V", "D", "DZ"]

FILE = DB_FOLDER / "urls.json"
SET_INDEX_FILE = DB_FOLDER / "set_index.json"

# Rarity may be absent in supplemental card packs; row length is checked by the parser.
REQUIRED_FIELDS = {
	0: "Code",
	1: "Name",
	2: "Grade",
	3: "Faction",
	4: "Type"
}

EVENTS = [
	PipelineEvent.SELECT_CATEGORY,
	PipelineEvent.SELECT_SUBCATEGORY,
	PipelineEvent.BUILD_QUERY,
	PipelineEvent.MAKE_CONSULT,
	PipelineEvent.CLEAN_RESULT,
	PipelineEvent.MAIN_ROUTINE
]

CARD_TABLE_HEADERS = {
	"CardList/header": "card",
	"CardList/header/V": "card",
	"CardList/header/D": "card",
	"CardList/header/TD": "deck",
	"CardList/header/TD/D": "deck",
}

CARD_TABLE_FOOTERS = {"Footer", "CardList/footer"}
CARD_ROW_TEMPLATES = {"CardList", "CardListV", "CardListV/TD", "CardListD", "CardList2", "CardList2N"}

OPTIONS = {
	0: "boosters",
	1: "specials",
	2: "decks",
	3: "others",
	4: "cards"
}
