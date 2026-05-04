# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    pipeline.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/04 16:19:46 by marvin            #+#    #+#              #
#    Updated: 2026/05/04 16:19:46 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing import List, Union, Literal
import re

# Dependencies
import requests

# Definition
JSONType = dict[str]

# Classes
class	MediaWikiAPI:
	"""
	Class that contains the url for API request. It exist to make HTTP requests only.
	"""
	API_URL = "https://cardfight.fandom.com/api.php"

	def	__init__(self):
		self.session = requests.Session()

	def	get(self,
			params: dict[str, Union[str, List[str]]],
			headers: dict[str, str]) -> JSONType:
		"""
		Function to obtain information from the MediaWikiAPI. In order to use it, you
		must define ther correct HTTP parameter. The returned data will have a json structure.

		Parameters:
			params: necesary parameters to make a request to the API. Please consult https://www.mediawiki.org/wiki/API:Action_API.
			headers: HTTP headers (such as User-Agent).

		Returns:
			JSONType: If the request was succesful, you will have a json file with the desired information.
		"""
		return (
			self.session.get(	
			self.API_URL,
			params=params,
			headers=headers
			).json()
		)

class	VanguardScrapper:
	def	__init__(self, api: MediaWikiAPI):
		self.api = api

	def	obtain_links(self, data: JSONType):
		sets = []
		for link in data["parse"]["links"]:
			if (link.get("ns") == 0):
				sets.append(link["*"])
		return (sets)
	
	def	obtain_wikitex(self, curl: JSONType) -> str:
		"""
		Function to obtain the content of a not parsed curl request to the MediaWikiAPI request.
		This function only work if the cards label information it's the same in this function
		('query', 'pages', 'revisions', 'slots', 'main', '*')
		* -> has cards info
		
		Parameters:
			curl: answer of the API.

		Returns:
			String with the wikidex information
		"""
		try:
			pages = curl.get("query", {}).get("pages", {})
			page = next(iter(pages.values()))
			return (page.get("revisions", {})[0].get("slots", {}).get("main", {}).get("*"))
		except (StopIteration, IndexError):
			return (None)
	
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

	def remove_from_list(self, sets: list, to_delete: list):
		return ([s for s in sets if not any(pattern in s for pattern in to_delete)])
	
	def __dict_construct(self, consult: Union[Literal["consult", "get"]], lst: list):
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
		else:
			return {
				value: {
					"action": "parse",
					"page": value,
					"format": "json"
				}
				for _, value in enumerate(lst)
			}
	
	def __cleaners_construct(self, curl_parsed: list):
		self.key_cleaners = {}
		for k, v in enumerate(curl_parsed):
			match = next(
				(w for w in curl_parsed[k].lower().split() if w in self._KEYWORD),
				None
			)
			self.key_cleaners[v] = match.capitalize() if match else None
	
	def make_consults(self, consult: Union[Literal["consult", "get"]], lst: list):
		return (self.__dict_construct(consult, lst))
	
	def	clean_trash_from_set(self, curl_parsed: list, crude: list, index: int):
		self.__cleaners_construct(curl_parsed)
		key = curl_parsed[index]
		for i in range(len(crude) - 1, -1, -1):
			value = crude[i]
			if (self.key_cleaners[key] not in value):
				crude.remove(value)

class	VanguardClassifier:
	def	__init__(self):
		self._rules = [
			(r"^DZ", "DZ"),
			(r"^D", "D"),
			(r"^G", "G"),
			(r"^V", "V"),
			(r"^Booster", "LB")
		]

	def	obtain_set_number(self, play_set: str):
		number = ""
		for i in play_set:
			if (i.isdigit()):
				number += i
			elif (number):
				break
		return (int(number))

	def	classify(self, name: str) -> str:
		num = self.obtain_set_number(name)
		if (num in (16, 17) and "Booster" in name):
			return ("LL")
		for pattern, key in self._rules:
			if (re.match(pattern, name)):
				return (key)
		return ("LB")

class	VanguardStorage:
	def __init__(self):
		self.seen = {
			"LB": set(), "LL": set(), "G": set(),
			"V": set(), "D": set(), "DZ": set()
		}
		self.lb =		[]
		self.ll =		[]
		self.g =		[]
		self.v =		[]
		self.d =		[]
		self.dz	=		[]

	def _add_item(self, key: str, item: str):
		if item not in self.seen[key]:
			self.seen[key].add(item)
			getattr(self, key.lower()).append(item)

class	VanguardPipeline:
	def	__init__(self, scrapper, parser, classifier, storage):
		self.scrapper =	scrapper
		self.parser = parser
		self.classifier = classifier
		self.storage = storage
