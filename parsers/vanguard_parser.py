# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_parser.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:17:03 by marvin            #+#    #+#              #
#    Updated: 2026/08/09 22:03:29 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.nodes		import Template
from mwparserfromhell.wikicode	import Wikicode

# Library
from utils.constants			import DICT_S
from pipeline.builder			import VanguardPipeline
from scrapper.fsm				import ParseContext as Context
from utils.utils				import clean_text, remove_from_list
from classifier.classifier		import process_items, sort_storage_list

class	VanguardParser:
	def	__init__(self):
		self.pipeline = VanguardPipeline()

	def separate_urls(self, data: list):
		no_main_sets = []
		for i in range(len(data) - 1, -1, -1):
			value = data[i]
			if ("Booster" not in value or "Cardfight!!" in value or "Unique" in value):
				no_main_sets.append(data.pop(i))
		return (no_main_sets)
	
	def	clean_trash_from_set(self, curl_parsed: str, crude: list, index: int,
						  reverse: bool = False):
		cleaner = curl_parsed.split()[index]
		if (cleaner is None):
			return (None)
		for i in range(len(crude) - 1, -1, -1):
			value = crude[i]
			if (not reverse):
				if (cleaner not in value):
					crude.remove(value)
			else:
				if (cleaner in value):
					crude.remove(value)
	
	def __process_infobox(self, tpl: Template, data: dict):
		titles = {}
		infos = {}

		for param in tpl.params:
			name = str(param.name).strip().lower()
			value = str(param.value).strip()
			value = value.replace("<br/>", "").replace("<br>", "")

			if "title" in name:
				idx = "".join([c for c in name if c.isdigit()])
				titles[idx] = value.lower()

			elif "info" in name:
				idx = "".join([c for c in name if c.isdigit()])
				infos[idx] = value

		for idx in infos:
			if idx in titles:
				data[titles[idx]] = infos[idx]
		return (data)
		
	def	infobox(self, parsed: Wikicode) -> dict:
		box = {}
		for tpl in parsed.filter_templates():
			if ("Infobox" in tpl.name):
				box = self.__process_infobox(tpl, box)
		return (box)

	def sort_unique_url(self, parsed_cardlist: list[Template], crude_links: list[str]):
		links = {}
		used = set()

		for _, card in enumerate(parsed_cardlist):
			card_name = clean_text(str(card.params[1].value).strip())

			for link in crude_links:
				clean_link = clean_text(link)
				if card_name in clean_link and clean_link not in used:
					links[clean_link] = clean_link
					used.add(clean_link)
					break
		return (links)

	def	parse_links(self, ctx: Context, pipeline: VanguardPipeline):
		links = pipeline.scrapper.obtain_links(ctx.response)
		self.pipeline.parser.clean_trash_from_set(ctx.response, links, 4)
		parsed_links = remove_from_list(links, [
			ctx.response,
			*DICT_S.get(ctx.response)
		])
		process_items(parsed_links, self.pipeline)
		if (ctx.category == "boosters"):
			sort_storage_list(["LB", "G"], self.pipeline)
		sort_storage_list(["LB", "LL", "G", "V", "D", "DZ"], self.pipeline)

	def	parser(self, card_fsm: CardFSM, pipeline: VanguardPipeline):
		wikitex = pipeline.scrapper.obtain_wikitex(card_fsm.fsm_context.data["api_result"])
		card_fsm.fsm_context.data["crude_cards"] = pipeline.scrapper.make_cardlist_from_str(wikitex)
		card_fsm.context.infobox = pipeline.parser.infobox(wikitex)
		all_links = pipeline.scrapper.obtain_links(card_fsm.fsm_context.data["link_result"])
		pipeline.parser.clean_trash_from_set(card_fsm.fsm_context.data["page"], all_links, 4, reverse=True)
		card_fsm.context.links = pipeline.parser.sort_unique_url(
			card_fsm.fsm_context.data["crude_cards"], all_links
		)