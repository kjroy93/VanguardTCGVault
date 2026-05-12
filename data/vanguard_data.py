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
from cards.fsm				import CardFSM
from cards.classes			import ScrapCard, ScrapDeck

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

	def _add_item(self, key: str, item: str):
		if item not in self._seen[key]:
			self._seen[key].add(item)
			getattr(self, key.lower()).append(item)

	def	__construct_decks(self, fsm: CardFSM) -> object:
		try:
			row = fsm.context.obj(
				CardNo =		fsm.context.row[0],
				Amount =		fsm.context.row[1],
				Name =			fsm.context.row[2],
				Grade = 		fsm.context.row[3],
				Faction =		[fsm.context.row[4]],
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[5],
				Release = 		fsm.context.infobox.get("release date") or
									fsm.context.infobox.get("release date:") or ""
			)
			return (row)
		except (IndexError, ValueError):
			row = fsm.context.obj(
				CardNo =		"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		fsm.context.infobox.get("release date") or
									fsm.context.infobox.get("release date:") or ""
			)
			return (row)
	
	def	__construct_rows(self, fsm: CardFSM) -> object:
		try:
			row = fsm.context.obj(
				CardNo =		fsm.context.row[0],
				Name =			fsm.context.row[1],
				Grade =			fsm.context.row[2],
				Faction =		[fsm.context.row[3]],
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[4],
				Rarity = 		fsm.context.row[5],
				Release = 		fsm.context.infobox.get("release date") or
									fsm.context.infobox.get("release date:") or ""
			)
			return (row)
		except (IndexError, ValueError):
			row = fsm.context.obj(
				CardNo =		"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		fsm.context.infobox.get("release date") or
									fsm.context.infobox.get("release date:") or ""
			)
			return (row)

	def	prepare_data(self, list_of_wikitex: list[Template],
					fsm: CardFSM) -> list:
		handlers = {
			0: self.__construct_decks,
			1: self.__construct_rows
		}
		fsm.context.obj = ScrapDeck if fsm.context.is_deck else ScrapCard
		for i in range(0, len(list_of_wikitex)):
			fsm.run(list_of_wikitex[i].params)
			handler = handlers[fsm.context.prepare_data]
			fsm.context.row = handler(fsm)
			fsm.context.rows.append(fsm.context.row)
		data = [fsm.context.obj.model_dump() for fsm.context.obj in fsm.context.rows]
		return (data)
