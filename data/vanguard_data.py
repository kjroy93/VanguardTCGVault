# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/10/18 02:09:47 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import json

# Dependencies
import pandas					as pd
from mwparserfromhell.nodes		import Template

# Library
from data.set_index				import SetIndex
from utils.utils				import clean_text
from parsers.row_factory		import RowFactory
from routine.fsm				import SetContext
from parsers.cards_parser		import CardsParser
from cards.fsm					import CardContext
from data.update_database		import LinkStorage
from parsers.types				import MetadataType
from utils.constants			import FAILURE_FILE, SET_INDEX_FILE
from routine.metadata_routine	import MetadataRoutine
from data						import check_data_base
from cards.classes				import ScrapCard, ScrapDeck

HANDLERS = {
	MetadataType.DECK:		RowFactory.construct_decks,
	MetadataType.SINGLE:	RowFactory.construct_row,
	MetadataType.DUAL:		RowFactory.construct_rows
}

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
		card_parser = 		CardsParser()
		self.metadata = 	MetadataRoutine(card_parser)
		self.link_storage =	LinkStorage()
		self.set_index =	SetIndex(SET_INDEX_FILE)

	def _add_item(self, key: str, item: str):
		if item not in self._seen[key]:
			self._seen[key].add(item)
			getattr(self, key.lower()).append(item)

	def	check_existence(self, set_ctx: SetContext, arguments: dict):
		if (set_ctx.set_code is None and set_ctx.tpl is not None):
			set_ctx.set_code = self.set_index.get(set_ctx.tpl["titles"])
		if (set_ctx.set_code is None):
			return False
		if (check_data_base.set_exists(
			set_ctx, block=arguments["block"]
		)):
			self._remember_set_code(set_ctx)
			print(
				f"Skipping existing set: {set_ctx.set_code}"
			)
			return (True)
		return (False)

	def _remember_set_code(self, set_ctx: SetContext):
		if (set_ctx.tpl is not None and set_ctx.set_code is not None):
			self.set_index.remember(set_ctx.tpl["titles"], set_ctx.set_code)

	def obtain_url(self, text: str, set_ctx: SetContext, card_ctx: CardContext):
		url = set_ctx.card_page_titles_by_name.get(text)
		if (url is None):
			raise KeyError(f"URL not found for card: {text}")
		card_ctx.url = url

	def	manage_url(self, url, next_id, ctx: CardContext):
		set_id, is_new = self.link_storage.get_or_create(url, next_id)
		ctx.id = set_id
		ctx.url = url
		ctx.already_scraped = not is_new
		if (is_new):
			self.next_id += 1

	def	prepare_metadata(self,
					  wikitex: list[Template],
					  set_ctx: SetContext) -> list:

		self.next_id = len(self.link_storage._links)
		if (len(wikitex) != len(set_ctx.card_entries) or any(
			template != entry[1]
			for template, entry in zip(wikitex, set_ctx.card_entries)
		)):
			raise ValueError("Extract card tables with make_cardlist_from_str(wikitext, set_ctx) first")
		for table_kind, template in set_ctx.card_entries:
			card_ctx = CardContext()
			card_ctx.card = template.params
			card_ctx.name = str(template.name).strip()
			card_ctx.table_kind = table_kind
			card_ctx.id = self.next_id
			card_ctx.size = len(card_ctx.card)
			self.obtain_url(clean_text(str(template.params[1])).strip(), set_ctx, card_ctx)
			self.manage_url(card_ctx.url, card_ctx.id, card_ctx)
			self.metadata.run(card_ctx, set_ctx)
			card_ctx.obj = (ScrapDeck if table_kind == "deck" else ScrapCard)
			handler = HANDLERS[card_ctx.prepare_data]
			handler(card_ctx, set_ctx)

		data = [
			row.model_dump()
			for row in set_ctx.rows
		]
		set_ctx.rows.clear()
		return (data)

	def	create_dataframe(self, arguments: dict, set_ctx: SetContext, columns: list[str]):
		df = pd.DataFrame(arguments.get("data"), columns=columns)
		path = check_data_base.build_set_path(
			set_ctx, block=arguments["block"]
		)
		path.parent.mkdir(
			parents=True,
			exist_ok=True
		)
		try:
			output = path.open("xb")
		except FileExistsError:
			self._remember_set_code(set_ctx)
			print(f"Skipping existing set: {set_ctx.set_code}")
			return
		try:
			with output:
				df.to_parquet(output)
		except BaseException:
			# An interrupted write must not be mistaken for a complete set.
			path.unlink()
			raise
		self._remember_set_code(set_ctx)
		print(df)

	def	failure_routine(self,
					 lst: list,
					 set_ctx: SetContext,
					 saved_urls: set,
					 error_mesage: str):

		lst.append(
			{
				"set": set_ctx.tpl.get("titles"),
				"error": str(error_mesage)
			}
		)
		self.link_storage.rollback(saved_urls)
		set_ctx.rows.clear()
		set_ctx.is_deck = False

	def	json_with_failures(self, failed_sets: list[dict]):
		with open(FAILURE_FILE, "w") as file:
			json.dump(failed_sets, file, indent=4)
