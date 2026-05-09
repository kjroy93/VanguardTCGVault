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

from mwparserfromhell.nodes	import Template
from cards.classes			import ScrapCard, ScrapDeck
from parsers.normalizers	import normalize_length, raw_table_data_prepare

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
	
	def	__construct_rows(self, data: list[str | int],
					  obj: type[ScrapCard | ScrapDeck],
					  is_d: bool,
					  infobox: dict) -> object:
		print(data)
		try:
			row = obj(
				CardNo =		data[0],
				Name =			data[1],
				Grade =			data[2],
				Faction =		data[3],
				FactionType =	"Nation" if is_d else "Clan",
				Type = 			data[4],
				Rarity = 		data[5],
				Release = 		infobox.get("release date:") or ""
			)
			return (row)
		except (IndexError, ValueError):
			row = obj(
				CardNo =		"None",
				Name =			"None",
				Grade =			0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		infobox.get("release date:") or "None"
			)
			return (row)
		
	def	prepare_data(self, list_of_wikitex: list[Template],
				size: int,
				is_deck: bool = False,
				is_d: bool = False,
				infobox: dict = None) -> list:
		rows = []
		for i in range(0, len(list_of_wikitex)):
			parsed_row = normalize_length(list_of_wikitex[i].params, size)
			parsed_row = raw_table_data_prepare(list_of_wikitex[i].params, size)
			obj = ScrapCard if is_deck else ScrapDeck
			row = self.__construct_rows(parsed_row, obj, is_d, infobox)
			rows.append(row)
		data = [obj.model_dump() for obj in rows]
		return (data)