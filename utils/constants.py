# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    constants.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/13 11:54:05 by marvin            #+#    #+#              #
#    Updated: 2026/08/15 16:06:59 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from pathlib	import Path

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
	"Stoicheia",
	"Dark States",
	"Keter Sanctuary",
	"Brandt Gate"
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
		"Thailand"
	],
	"decks": [
		"List",
		"Thailand"
	]
}

SET_PATHS = {
	"boosters": {
		"booster": {
			"folder": "boosters/booster sets",
			"prefix": "set"
		},
		"extra": {
			"folder": "boosters/extra booster sets",
			"prefix": "extra"
		},
		"character": {
			"folder": "boosters/character booster sets",
			"prefix": "character"
		},
		"clan": {
			"folder": "boosters/clan booster sets",
			"prefix": "clan"
		},
		"title": {
			"folder": "boosters/title booster sets",
			"prefix": "title"
		},
		"unique": {
			"folder": "boosters/unique booster sets",
			"prefix": "unique"
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
VALID_DATABASES = ["LB", "LL", "G", "V", "D", "DZ"]

FILE = DB_FOLDER / "urls.json"
