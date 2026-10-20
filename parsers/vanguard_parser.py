# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_parser.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:17:03 by marvin            #+#    #+#              #
#    Updated: 2026/10/18 03:21:31 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
from typing 					import Union, Literal

# Dependencies
from mwparserfromhell.nodes		import Template
from mwparserfromhell.wikicode	import Wikicode

# Library
from routine.fsm 				import SetContext
from utils.utils				import clean_text, make_custom_alphabet
from utils.constants 			import CARD_TABLE_HEADERS, CARD_TABLE_FOOTERS, CARD_ROW_TEMPLATES

class	VanguardParser:
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

			if ("title" in name):
				idx = "".join([c for c in name if c.isdigit()])
				titles[idx] = value.lower()

			elif ("info" in name):
				idx = "".join([c for c in name if c.isdigit()])
				infos[idx] = value

		for idx in infos:
			if (idx in titles):
				data[titles[idx]] = infos[idx]
		return (data)
		
	def	infobox(self, parsed: Wikicode) -> dict:
		box = {}
		for tpl in parsed.filter_templates():
			if ("Infobox" in tpl.name):
				box = self.__process_infobox(tpl, box)
		return (box)

	def sort_unique_url(self, parsed_cardlist: list[Template], candidate_card_page_titles: list[str]):
		card_page_titles_by_name = {}
		card_page_titles_by_initial = make_custom_alphabet(candidate_card_page_titles)

		for _, card in enumerate(parsed_cardlist):
			card_name = clean_text(str(card.params[1].value).strip())
			if (not card_name):
				raise TypeError(f"Card name cannot be empty {card.params}")
			letter = card_name[0]
			if (letter not in card_page_titles_by_initial):
				continue
			matched_page_title = card_page_titles_by_initial[letter].get(card_name)
			if (matched_page_title is None):
				matching_page_titles = [
					original_page_title
					for normalized_page_title, original_page_title in card_page_titles_by_initial[letter].items()
					if card_name in normalized_page_title
				]
				if (len(matching_page_titles)) == 1:
					matched_page_title = matching_page_titles[0]
			if (matched_page_title is not None):
				card_page_titles_by_name[card_name] = matched_page_title
		return (card_page_titles_by_name)

	def make_consults(self, lst: list, format: Literal["consult", "decks"]) -> dict[int, dict[str, str]]:
		def __dict_construct(consult: Union[Literal["consult", "decks"]], lst: list):
			if (consult == "consult"):
				return {
					i: {
					"action": "query",
					"format": "json",
					"prop": "revisions",
					"titles": value,
					"rvprop": "content",
					"rvslots": "main"
				}
				for i, value in enumerate(lst)
			}
			if (consult == "decks"):
				return {
					i: {
					"action": "parse",
					"page": value,
					"prop": "text",
					"format": "json"
					}
					for i, value in enumerate(lst)
				}
			else:
				return {
					value: {
						"action": "parse",
						"page": value,
						"format": "json"
					}
					for _, value in enumerate(lst)
				}
		return (__dict_construct(format, lst))

	@staticmethod
	def get_set_code(cards: list[Template], block: str) -> str:
		if (not cards):
			raise ValueError("Cannot determine set code without cards")
		card_code = str(cards[0].get("1").value).strip()
		match = re.match(r"^([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)/", card_code)
		if (match is None):
			raise ValueError(f"Invalid code in first card of main table: {card_code!r}")
		if (block == "LB" or block == "LL"):
			return (block + "-" + match.group(1).upper())
		return (match.group(1).upper())

	def	make_cardlist_from_str(self, wikitex: Wikicode, set_ctx: SetContext | None = None):
		if (set_ctx is not None):
			set_ctx.set_code = None
		card_entries = []
		table_kind = None
		for tpl in wikitex.filter_templates():
			name = str(tpl.name).strip()
			if (name in CARD_TABLE_HEADERS):
				table_kind = CARD_TABLE_HEADERS[name]
				continue
			if (name in CARD_TABLE_FOOTERS):
				table_kind = None
				continue
			if (name.startswith("CardList/header")):
				raise ValueError(f"Unknown card table header: {name}")
			if (name in CARD_ROW_TEMPLATES):
				if (table_kind is None):
					raise ValueError(f"Card outside a recognized table: {tpl}")
				card_entries.append((table_kind, tpl))
			elif (name.startswith("CardList")):
				raise ValueError(f"Unknown card template: {name}")
		cards = [tpl for _, tpl in card_entries]
		if (set_ctx is not None):
			set_ctx.set_code = self.get_set_code(cards, set_ctx.block)
			set_ctx.card_entries = card_entries
			set_ctx.crude_cards = cards
			set_ctx.is_deck = bool(card_entries) and all(
				table_kind == "deck" for table_kind, _ in card_entries
			)
		return (cards)
