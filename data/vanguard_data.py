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

import json
import os

# Dependencies
from mwparserfromhell.nodes	import Template

# Library
from utils					import utils
from cards.fsm				import CardFSM
from cards.states			import ParserState
from cards.classes			import ScrapCard, ScrapDeck

DATA_DIR = "database"
FILE = os.path.join(DATA_DIR ,"urls.json")

class	LinkStorage:
	def	__load_data(self):
		if (os.path.exists(FILE)):
			with open(FILE, "r", encoding="utf-8") as f:
				return (json.load(f))
		return ({})

	def	__init__(self):
		self._links = self.__load_data()

	def	__save_data(self):
		with open(FILE, "w", encoding="utf-8") as f:
			json.dump(self._links, f, indent=4, ensure_ascii=False)

	def	register_link(self, index: int, url: str) -> bool:
		if (url in self._links):
			return (self._links[url], False)
		self._links[url] = index
		self.__save_data()
		return (index, True)
	
	def	define_url(self, fsm: CardFSM):
		stored_index, is_new = (self.register_link(
			fsm.context.index, fsm.context.url))
		fsm.context.index = stored_index
		fsm.context.is_duplicated = not is_new
		if (fsm.context.is_duplicated):
			fsm.context.url_ref = stored_index
		else:
			fsm.context.url_ref = str(fsm.context.url).strip()

class	RowFactory:
	@staticmethod
	def	get_release(info: dict) -> str:
		return (
			info.get("release date")
			or info.get("release date:")
			or "Unknown"
		)

	@staticmethod
	def	construct_decks(fsm: CardFSM) -> object:
		release = RowFactory.get_release(fsm.context.infobox)
		try:
			row = fsm.context.obj(
				Code =			fsm.context.row[0],
				Amount =		fsm.context.row[1],
				Name =			fsm.context.row[2],
				Grade = 		fsm.context.row[3],
				Faction =		[fsm.context.row[4]],
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[5],
				Release = 		release,
				URL =			str(fsm.context.url).strip()
			)
			return (row)
		except (IndexError, ValueError):
			row = fsm.context.obj(
				Code =			"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		release,
				URL =			"None"
			)
			return (row)

	@staticmethod
	def	construct_row(fsm: CardFSM) -> object:
		release = RowFactory.get_release(fsm.context.infobox)
		try:
			row = fsm.context.obj(
				Code =			fsm.context.row[0],
				Name =			fsm.context.row[1],
				Grade =			fsm.context.row[2],
				Faction =		[fsm.context.row[3]],
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[4],
				Rarity = 		fsm.context.row[5],
				Release = 		release,
				URL = 			fsm.context.url_ref
			)
			fsm.context.rows.append(row)
		except (IndexError, ValueError):
			row = fsm.context.obj(
				Code =			"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		release,
				URL =			"None"
			)
			fsm.context.rows.append(row)

	@staticmethod
	def	construct_rows(fsm: CardFSM):
		for i in range(len(fsm.context.row)):
			release = RowFactory.get_release(fsm.context.infobox)
			try:
				row = fsm.context.obj(
					Code =			fsm.context.row[i][0],
					Name =			fsm.context.row[i][1],
					Grade =			fsm.context.row[i][2],
					Faction =		[fsm.context.row[i][3]],
					FactionType =	"Nation" if fsm.context.is_d else "Clan",
					Type = 			fsm.context.row[i][4],
					Rarity = 		fsm.context.row[i][5],
					Release = 		release,
					URL = 			fsm.context.url_ref
				)
			except (IndexError, ValueError):
				row = fsm.context.obj(
					Code =			"None",
					Name =			"None",
					Grade =			0,
					Faction =		["None"],
					FactionType =	"None",
					Type = 			"None",
					Rarity = 		"None",
					Release = 		release,
					URL =			"None"
				)
			fsm.context.rows.append(row)
			fsm.context.index += 1

class	VanguardStorage:
	def __init__(self):
		self._seen = {
			"LB": set(), "LL": set(), "G": set(),
			"V": set(), "D": set(), "DZ": set()
		}
		self.lb =			[]
		self.ll =			[]
		self.g =			[]
		self.v =			[]
		self.d =			[]
		self.dz	=			[]
		self.row_factory =	RowFactory()
		self.link_storage =	LinkStorage()

	def _add_item(self, key: str, item: str):
		if item not in self._seen[key]:
			self._seen[key].add(item)
			getattr(self, key.lower()).append(item)

	def	obtain_url(self, text: str, fsm: CardFSM):
		text_word = set(text.split())
		for url in fsm.context.links.keys():
			url_words = set(url.split())
			if (text_word.issubset(url_words)):
				fsm.context.url = url
				break

	def	prepare_data(self, wikitex: list[Template],
					fsm: CardFSM) -> list:
		handlers = {
			0: RowFactory.construct_decks,
			1: RowFactory.construct_row,
			2: RowFactory.construct_rows
		}
		fsm.context.index = len(self.link_storage._links) - 1
		fsm.context.obj = ScrapDeck if fsm.context.is_deck else ScrapCard
		for template in wikitex:
			text = utils.clean_text(str(template.params[1]).strip())
			self.obtain_url(text, fsm)
			self.link_storage.define_url(fsm)
			fsm.run(template.params)
			handler = handlers[fsm.context.prepare_data]
			handler(fsm)
			if (fsm.context.is_duplicated):
				fsm.state = ParserState.START
				continue
			fsm.context.index += 1
			fsm.state = ParserState.START
		data = [fsm.context.obj.model_dump(exclude_none=True)
			for fsm.context.obj in fsm.context.rows]
		fsm.context.rows.clear()
		return (data)
