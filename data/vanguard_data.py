# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/08/17 03:51:52 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import json

# Dependencies
import pandas					as pd
from mwparserfromhell.nodes		import Template

# Library
from utils.utils				import clean_text
from parsers.row_factory		import RowFactory
from routine.fsm				import SetContext
from parsers.cards_parser		import CardsParser
from cards.fsm					import CardContext
from data.update_database		import LinkStorage
from parsers.types				import MetadataType
from utils.constants			import FAILURE_FILE
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

	def _add_item(self, key: str, item: str):
		if item not in self._seen[key]:
			self._seen[key].add(item)
			getattr(self, key.lower()).append(item)

	def obtain_url(self, text: str, set_ctx: SetContext, card_ctx: CardContext):
		url = set_ctx.links.get(text)
		if (url is None):
			raise KeyError(f"URL not found for card: {text}")
		card_ctx.url = url

	def	check_existence(self, set_ctx: SetContext, arguments: dict):
		if (check_data_base.set_exists(
			set_ctx, block=arguments.get("block"),
			set_number=arguments.get("set_number")
		)):
			print(
				f"Skiping existing set: "
				f"{arguments.get('block')} {arguments.get('set_number') + 1}"
			)
			return (True)
		return (False)

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
		for template in wikitex:
			card_ctx = CardContext()
			card_ctx.card = template.params
			card_ctx.id = self.next_id
			self.obtain_url(clean_text(str(template.params[1])).strip(), set_ctx, card_ctx)
			self.manage_url(card_ctx.url, card_ctx.id, card_ctx)
			self.metadata.run(card_ctx, set_ctx)
			card_ctx.obj = (ScrapDeck if set_ctx.is_deck else ScrapCard)
			handler = HANDLERS[card_ctx.prepare_data]
			handler(card_ctx, set_ctx)

		data = [
			row.model_dump(exclude_none=True)
			for row in set_ctx.rows
		]
		set_ctx.rows.clear()
		return (data)

	def	create_dataframe(self, arguments: dict, set_ctx: SetContext, columns: list[str]):
		df = pd.DataFrame(arguments.get("data"), columns=columns)
		path = check_data_base.build_set_path(
			category=set_ctx.category,
			set_type=set_ctx.subcategory.strip().lower().split()[0],
			block=arguments.get("block"),
			set_number=arguments.get("set_number") + 1
		)
		path.parent.mkdir(
			parents=True,
			exist_ok=True
		)
		path = check_data_base.get_duplicate_path(path)
		df.to_parquet(path)
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
		set_ctx.is_deck = False

	def	json_with_failures(self, failed_sets: list[dict]):
		with open(FAILURE_FILE, "w") as file:
			json.dump(failed_sets, file, indent=4)
