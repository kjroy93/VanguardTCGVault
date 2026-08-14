# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_data.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:31:47 by marvin            #+#    #+#              #
#    Updated: 2026/08/14 19:47:11 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.nodes	import Template

# Library
from utils						import utils
from parsers.row_factory		import RowFactory
from data.update_database		import LinkStorage
from scrapper.metadata_routine	import MetadataRoutine
from cards.classes				import ScrapCard, ScrapDeck
from scrapper.fsm				import PipelineContext as Context

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
		set_id, is_new = LinkStorage.get_or_create(url, next_id)
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
		self.next_id = len(LinkStorage._links)
		ctx.obj = ScrapDeck if ctx.is_deck else ScrapCard
		for template in wikitex:
			text = utils.clean_text(str(template.params[1]).strip())
			self.obtain_url(text, ctx)
			url = ctx.url
			self.manage_url(url, self.next_id, ctx)
			MetadataRoutine.run(template.params)
			handler = handlers[ctx.prepare_data]
			handler(ctx)
		data = [ctx.obj.model_dump(exclude_none=True)
			for ctx.obj in ctx.rows]
		ctx.rows.clear()
		return (data)
