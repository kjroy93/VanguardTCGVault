# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_parser.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:17:03 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:17:03 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from typing						import Literal

# Dependencies
from mwparserfromhell.nodes		import Template
from mwparserfromhell.wikicode	import Wikicode

# Library
from api_builder.api_request	import dict_construct

class	VanguardParser:
	def separate_urls(self, data: list):
		no_main_sets = []
		for i in range(len(data) - 1, -1, -1):
			value = data[i]
			if ("Booster" not in value or "Cardfight!!" in value or "Unique" in value):
				no_main_sets.append(data.pop(i))
		return (no_main_sets)
	
	def	clean_trash_from_set(self, curl_parsed: str, crude: list, index: int):
		cleaner = curl_parsed.split()[index]
		if (cleaner is None):
			return (None)
		for i in range(len(crude) - 1, -1, -1):
			value = crude[i]
			if (cleaner not in value):
				crude.remove(value)

	def make_consults(self, lst: list, format: Literal["consult", "decks"]):
		return (dict_construct(format, lst))
	
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

		return data
		
	def	infobox(self, parsed: Wikicode) -> dict:
		box = {}
		for tpl in parsed.filter_templates():
			if ("Infobox" in tpl.name):
				box = self.__process_infobox(tpl, box)
		return (box)
