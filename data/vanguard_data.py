# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/08/15 17:20:30 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.nodes		import Template

# Library
from utils.utils				import clean_text
from parsers.row_factory		import RowFactory
from scrapper.fsm				import SetContext
from parsers.cards_parser		import CardsParser
from cards.fsm					import CardContext
from data.update_database		import LinkStorage
from cards.classes				import ScrapCard, ScrapDeck
from scrapper.metadata_routine	import MetadataRoutine
from parsers.types				import MetadataType

handlers = {
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

	def	obtain_url(self, text: str, set_ctx: SetContext, card_ctx: CardContext):
		text_word = set(text.split())
		for url in set_ctx.links.keys():
			url_words = set(url.split())
			if (text_word.issubset(url_words)):
				card_ctx.url = url
				break

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
			handler = handlers[card_ctx.prepare_data]
			handler(card_ctx, set_ctx)

		data = [
			row.model_dump(exclude_none=True)
			for row in set_ctx.rows
		]
		set_ctx.rows.clear()
		return (data)
			