# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:31:47 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from typing					import Literal

# Dependencies
from mwparserfromhell.nodes	import Template

# Library
from cards.classes			import ScrapCard, ScrapDeck
from cards.fsm				import ParserContext

class	VanguardStorage:
	def __init__(self):
		self._seen = {
			"LB": set(), "LL": set(), "G": set(),
			"V": set(), "D": set(), "DZ": set()
		}
		self.lb =		[]
		self.ll =		[]
		self.g =		[]
		self.v =		[]
		self.d =		[]
		self.dz	=		[]
	
	def	__construct_decks(self, fsm: ParserContext) -> object:
		try:
			row = fsm.obj(
				CardNo =		fsm.row[0],
				Amount =		fsm.row[1],
				Name =			fsm.row[2],
				Grade = 		fsm.row[3],
				Faction =		[fsm.row[4]],
				FactionType =	"Nation" if fsm.is_d else "Clan",
				Type = 			fsm.row[5],
				Release = 		fsm.infobox.get("release date") or
									fsm.infobox.get("release date:") or ""
			)
			return (row)
		except (IndexError, ValueError):
			row = fsm.obj(
				CardNo =		"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		fsm.infobox.get("release date") or
									fsm.infobox.get("release date:") or ""
			)
			return (row)
	
	def	__construct_rows(self, fsm: ParserContext) -> object:
		try:
			row = fsm.obj(
				CardNo =		fsm.row[0],
				Name =			fsm.row[1],
				Grade =			fsm.row[2],
				Faction =		[fsm.row[3]],
				FactionType =	"Nation" if fsm.is_d else "Clan",
				Type = 			fsm.row[4],
				Rarity = 		fsm.row[5],
				Release = 		fsm.infobox.get("release date") or
									fsm.infobox.get("release date:") or ""
			)
			return (row)
		except (IndexError, ValueError):
			row = fsm.obj(
				CardNo =		"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		fsm.infobox.get("release date") or
									fsm.infobox.get("release date:") or ""
			)
			return (row)

	def	prepare_data(self, list_of_wikitex: list[Template],
				size: int,
				is_deck: bool = False,
				is_d: bool = False,
				infobox: dict = None,
				label: Literal["decks"] = None) -> list:
		rows = []
		handlers = {
			0: self.__construct_decks,
			1: self.__construct_rows
		}
		obj = ScrapDeck if is_deck else ScrapCard
		for i in range(0, len(list_of_wikitex)):
			n_row = normalize_length(list_of_wikitex[i].params, size)
			is_multiple = isinstance(n_row[0], list)
			handler = handlers[is_multiple]
			handler(n_row, rows, obj, is_d, infobox)
		data = [obj.model_dump() for obj in rows]
		return (data)
