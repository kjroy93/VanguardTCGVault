# Imports
from typing import List, Union, Tuple, Literal
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

class	VanguardParser:
	def separate_boosters(self, data: list):
		no_main_sets = []
		for i in range(len(data) - 1, -1, -1):
			value = data[i]
			if ("Booster" not in value or "Cardfight!!" in value or "Unique" in value):
				no_main_sets.append(data.pop(i))
		return (no_main_sets)

	def remove_from_list(self, sets: list, to_delete: list):
		for i in to_delete:
			if i in sets:
				sets.remove(i)
	
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
				i: {
					"action": "parse",
					"page": value,
					"format": "json"
				}
				for i, value in enumerate(lst)
			}
	
	def make_consults(self, consult: Union[Literal["consult", "get"]], lst: list):
		return (self.__dict_construct(consult, lst))

class	VanguardClassifier:
	def	__init__(self, rules: Union[list[Tuple[str, str]]]):
		self.rules = rules

	def	obtain_set_number(self, play_set: str):
		number = ""
		for i in play_set:
			if (i.isdigit()):
				number += i
			elif (number):
				break
		return (int(number))

	def	sort_sets(self, lst: list, element: str):
		num = self.obtain_set_number(element)
		i = 0
		while (i < len(lst)):
			if (self.obtain_set_number(lst[i]) > num):
				break
			i += 1
		if (element in lst):
			return ("")
		lst.insert(i, element)

	def	classify(self, name: str) -> str:
		num = self.obtain_set_number(name)
		if (num in (16, 17)):
			return ("LL")
		for pattern, key in self.rules:
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
