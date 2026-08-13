# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/08/13 20:09:28 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import json
import os

# Dependencies
from mwparserfromhell.nodes	import Template

# Library
from utils					import utils
from cards.classes			import ScrapCard, ScrapDeck
from scrapper.fsm			import ParseContext as Context

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
		try:
			with open(FILE, "w", encoding="utf-8") as f:
				json.dump(self._links, f, indent=4, ensure_ascii=False)
		except FileNotFoundError as e:
			print(f'Error {e} detected, creating file to save urls')
			os.mkdir(DATA_DIR)
			with open("urls.json", "w") as f:
				json.dump(self._links, f, ident=4, ensure_ascii=False)

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
	def	construct_decks(ctx: Context) -> object:
		release = RowFactory.get_release(ctx.infobox)
		faction = RowFactory.prepare_faction(ctx.row)
		try:
			row = ctx.obj(
				Code =			ctx.row[0],
				Amount =		ctx.row[1],
				Name =			ctx.row[2],
				Grade = 		ctx.row[3],
				Faction =		faction,
				FactionType =	"Nation" if ctx.is_d else "Clan",
				Type = 			ctx.row[5],
				Release = 		release,
			)
			ctx.rows.append(row)
		except (IndexError, ValueError):
			row = ctx.obj(
				Code =			"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		release,
			)
			ctx.rows.append(row)

	@staticmethod
	def	construct_row(ctx: Context) -> object:
		release = RowFactory.get_release(ctx.infobox)
		faction = RowFactory.prepare_faction(ctx.row)
		RowFactory.prepare_grade(ctx.row)
		try:
			row = ctx.obj(
				Code =			ctx.row[0],
				Name =			ctx.row[1],
				Grade =			ctx.row[2],
				Faction =		faction,
				FactionType =	"Nation" if ctx.is_d else "Clan",
				Type = 			ctx.row[4],
				Rarity = 		ctx.row[5],
				Release = 		release,
				URL = 			ctx.url,
				SET_ID =		int(ctx.id)
			)
			ctx.rows.append(row)
		except (IndexError, ValueError):
			row = ctx.obj(
				Code =			"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		release,
				URL =			ctx.url,
				SET_ID = 		int(ctx.id)
			)
			ctx.rows.append(row)

	@staticmethod
	def	construct_rows(ctx: Context):
		for i in range(len(ctx.row)):
			release = RowFactory.get_release(ctx.infobox)
			faction = RowFactory.prepare_faction(ctx.row[i])
			RowFactory.prepare_grade(ctx.row)
			try:
				row = ctx.obj(
					Code =			ctx.row[i][0],
					Name =			ctx.row[i][1],
					Grade =			ctx.row[i][2],
					Faction =		faction,
					FactionType =	"Nation" if ctx.is_d else "Clan",
					Type = 			ctx.row[i][4],
					Rarity = 		ctx.row[i][5],
					Release = 		release,
					URL = 			ctx.url,
					URL_ID =		int(ctx.id)
				)
			except (IndexError, ValueError):
				row = ctx.obj(
					Code =			"None",
					Name =			"None",
					Grade =			0,
					Faction =		["None"],
					FactionType =	"None",
					Type = 			"None",
					Rarity = 		"None",
					Release = 		release,
					URL =			ctx.url,
					URL_ID = 		int(ctx.id)
				)
			ctx.rows.append(row)
			ctx.id += 1

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

	def	obtain_url(self, text: str, ctx: Context):
		text_word = set(text.split())
		for url in ctx.links.keys():
			url_words = set(url.split())
			if (text_word.issubset(url_words)):
				ctx.url = url
				break

	def	manage_url(self, url, next_id, ctx: Context):
		set_id, is_new = self.link_storage.get_or_create(url, next_id)
		ctx.id = set_id
		ctx.url = url
		ctx.is_duplicated = not is_new
		if (is_new):
			self.next_id += 1
		else:
			ctx.url = None

	def	prepare_metadata(self, wikitex: list[Template],
					ctx: Context) -> list:
		handlers = {
			0: RowFactory.construct_decks,
			1: RowFactory.construct_row,
			2: RowFactory.construct_rows
		}
		self.next_id = len(self.link_storage._links)
		ctx.obj = ScrapDeck if ctx.is_deck else ScrapCard
		for template in wikitex:
			text = utils.clean_text(str(template.params[1]).strip())
			self.obtain_url(text, ctx)
			url = ctx.url
			self.manage_url(url, self.next_id, ctx)
			run(template.params)
			handler = handlers[ctx.prepare_data]
			handler(ctx)
		data = [ctx.obj.model_dump(exclude_none=True)
			for ctx.obj in ctx.rows]
		ctx.rows.clear()
		return (data)
