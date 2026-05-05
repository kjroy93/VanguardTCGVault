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

from typing import Union, Literal
from api_builder.api_request import dict_construct
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Template

class	VanguardParser:
	def	__init__(self):
		self._KEYWORD = {
			"trial", "title", "technical",
			"structure", "start", "special",
			"revival", "legend", "deck", "fighters",
			"extra", "collector's", "clan",
			"character", "combination", "thailand"
		}

	def separate_urls(self, data: list):
		no_main_sets = []
		for i in range(len(data) - 1, -1, -1):
			value = data[i]
			if ("Booster" not in value or "Cardfight!!" in value or "Unique" in value):
				no_main_sets.append(data.pop(i))
		return (no_main_sets)
	
	def __cleaners_construct(self, curl_parsed: list):
		key_cleaners = {}
		for k, v in enumerate(curl_parsed):
			match = next(
				(w for w in curl_parsed[k].lower().split() if w in self._KEYWORD),
				None
			)
			key_cleaners[v] = match.capitalize() if match else None
		return (key_cleaners)
	
	def	clean_trash_from_set(self, curl_parsed: list, crude: list, index: int):
		key_cleaners = self.__cleaners_construct(curl_parsed)
		key = curl_parsed[index]
		for i in range(len(crude) - 1, -1, -1):
			value = crude[i]
			if (key_cleaners[key] not in value):
				crude.remove(value)

	def make_consults(self, consult: Union[Literal["consult", "get"]], lst: list):
		return (dict_construct(consult, lst))
	
	def	__process_infobox(self, tpl: Template, data: dict):
		title = None
		for param in tpl.params:
			name = str(param.name).strip().lower()
			value = str(param.value).strip()
			if ("title" in name):
				title = value.lower()
			elif ("info" in name and title):
				data[title] = value.replace("<br>", "")
		return (data)
	
	def	infobox(self, parsed: Wikicode) -> dict:
		box = {}
		for tpl in parsed.filter_templates():
			if ("Infobox" in tpl.name):
				box = self.__process_infobox(tpl, box)
		return (box)
