# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_parser.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:17:03 by marvin            #+#    #+#              #
#    Updated: 2026/08/15 23:13:33 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing 					import Union, Literal

# Dependencies
from mwparserfromhell.nodes		import Template
from mwparserfromhell.wikicode	import Wikicode

# Library
from utils.utils				import clean_text, remove_from_list

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
		alphabet = {}
		
		for link in crude_links:
			clean_link = clean_text(link)
			if (not clean_link):
				continue
			letter = clean_link[0]
			if (letter not in alphabet):
				alphabet[letter] = {}
			alphabet[letter][clean_link] = link

		for _, card in enumerate(parsed_cardlist):
			card_name = clean_text(str(card.params[1].value).strip())
			if (not card_name):
				raise TypeError("Card name cannot be empty")
			letter = card_name[0]
			if (letter not in alphabet):
				continue
			link = alphabet[letter].get(card_name)
			if (link is not None):
				links[card_name] = link
		return (links)

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

	def	make_cardlist_from_str(self, wikitex: Wikicode):
		lst = []
		for tpl in wikitex.filter_templates():
			if ("CardList" in tpl.name):
				lst.append(tpl)
		lst = remove_from_list(lst, ["{{CardList/header/D}}",
							   "{{CardList/footer}}", "{{CardList/header}}",
							   "{{CardList/header/V}}"
							])
		return (lst)
