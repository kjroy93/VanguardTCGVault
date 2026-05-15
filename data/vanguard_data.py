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

	def get_or_create(self, url: str, next_id: int) -> tuple[int, bool]:
		url = url.strip()

		if (url in self._links):
			return (self._links[url], False)

		self._links[url] = next_id
		self.__save_data()
		return (next_id, True)

class	RowFactory:
	@staticmethod
	def	get_release(info: dict) -> str:
		return (
			info.get("release date")
			or info.get("release date:")
			or "Unknown"
		)

	@staticmethod
	def	prepare_faction(row: list):
		if (isinstance(row[3], list)):
			return (row[3])
		if (row[3] == '-'):
			return (["None"])
		return ([row[3]])

	@staticmethod
	def	prepare_grade(row: list):
		if (row[2] == '' or row[2] == '-'):
			row[2] = 0

	@staticmethod
	def	construct_decks(fsm: CardFSM) -> object:
		release = RowFactory.get_release(fsm.context.infobox)
		faction = RowFactory.prepare_faction(fsm.context.row)
		try:
			row = fsm.context.obj(
				Code =			fsm.context.row[0],
				Amount =		fsm.context.row[1],
				Name =			fsm.context.row[2],
				Grade = 		fsm.context.row[3],
				Faction =		faction,
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[5],
				Release = 		release,
			)
			fsm.context.rows.append(row)
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
			)
			fsm.context.rows.append(row)

	@staticmethod
	def	construct_row(fsm: CardFSM) -> object:
		release = RowFactory.get_release(fsm.context.infobox)
		faction = RowFactory.prepare_faction(fsm.context.row)
		RowFactory.prepare_grade(fsm.context.row)
		try:
			row = fsm.context.obj(
				Code =			fsm.context.row[0],
				Name =			fsm.context.row[1],
				Grade =			fsm.context.row[2],
				Faction =		faction,
				FactionType =	"Nation" if fsm.context.is_d else "Clan",
				Type = 			fsm.context.row[4],
				Rarity = 		fsm.context.row[5],
				Release = 		release,
				URL = 			fsm.context.url,
				SET_ID =		int(fsm.context.id)
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
				URL =			fsm.context.url,
				SET_ID = 		int(fsm.context.id)
			)
			fsm.context.rows.append(row)

	@staticmethod
	def	construct_rows(fsm: CardFSM):
		for i in range(len(fsm.context.row)):
			release = RowFactory.get_release(fsm.context.infobox)
			faction = RowFactory.prepare_faction(fsm.context.row[i])
			RowFactory.prepare_grade(fsm.context.row)
			try:
				row = fsm.context.obj(
					Code =			fsm.context.row[i][0],
					Name =			fsm.context.row[i][1],
					Grade =			fsm.context.row[i][2],
					Faction =		faction,
					FactionType =	"Nation" if fsm.context.is_d else "Clan",
					Type = 			fsm.context.row[i][4],
					Rarity = 		fsm.context.row[i][5],
					Release = 		release,
					URL = 			fsm.context.url,
					URL_ID =		int(fsm.context.id)
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
					URL =			fsm.context.url,
					URL_ID = 		int(fsm.context.id)
				)
			fsm.context.rows.append(row)
			fsm.context.id += 1

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

	def	manage_url(self, url, next_id, fsm: CardFSM):
		set_id, is_new = self.link_storage.get_or_create(url, next_id)
		fsm.context.id = set_id
		fsm.context.url = url
		fsm.context.is_duplicated = not is_new
		if (is_new):
			self.next_id += 1
		else:
			fsm.context.url = None

	def	prepare_data(self, wikitex: list[Template],
					fsm: CardFSM) -> list:
		handlers = {
			0: RowFactory.construct_decks,
			1: RowFactory.construct_row,
			2: RowFactory.construct_rows
		}
		self.next_id = len(self.link_storage._links)
		fsm.context.obj = ScrapDeck if fsm.context.is_deck else ScrapCard
		for template in wikitex:
			text = utils.clean_text(str(template.params[1]).strip())
			self.obtain_url(text, fsm)
			url = fsm.context.url
			self.manage_url(url, self.next_id, fsm)
			fsm.run(template.params)
			handler = handlers[fsm.context.prepare_data]
			handler(fsm)
			fsm.state = ParserState.START
		data = [fsm.context.obj.model_dump(exclude_none=True)
			for fsm.context.obj in fsm.context.rows]
		fsm.context.rows.clear()
		fsm.state = ParserState.END
		return (data)
