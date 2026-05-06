# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    api_request.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:24:34 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:24:34 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing import List, Union

# Dependencies
import aiohttp
import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

# Libraries
from utils.utils import remove_from_list

# Definitions
JSONType = dict[str]

# Classes
class	MediaWikiAPI:
	"""
	Class that contains the url for API request. It exist to make HTTP requests only.
	"""
	API_URL = "https://cardfight.fandom.com/api.php"

	def	__init__(self):
		self.session = None
	
	async def	init_session(self):
		self.session = aiohttp.ClientSession()
	
	async def	close_session(self):
		await self.session.close()

	async def	get(self,
			params: dict[str, Union[str, List[str]]],
			headers: dict[str, str]) -> JSONType:
		"""
		Function to obtain information from the MediaWikiAPI. In order to use it, you
		must define ther correct HTTP parameter. The returned data will have a json structure.

		Parameters:
			params: necesary parameters to make a request to the API.
			Please consult https://www.mediawiki.org/wiki/API:Action_API.
			headers: HTTP headers (such as User-Agent).

		Returns:
			JSONType: If the request was succesful, you will have a json file with the desired information.
		"""
		async with self.session.get(
			self.API_URL,
			params=params,
			headers=headers
		) as response:
			return (await response.json())

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
			return (mwparserfromhell.parse(page.get("revisions", {})[0].get("slots", {}).get("main", {}).get("*")))
		except (StopIteration, IndexError):
			return (None)
	
	def	make_cardlist_from_str(self, wikitex: Wikicode):
		lst = []
		for tpl in wikitex.filter_templates():
			if ("CardList" in tpl.name):
				lst.append(tpl)
		lst = remove_from_list(lst, ["{{CardList/header/D}}",
							   "{{CardList/footer}}", "{{CardList/header}}"
							])
		return (lst)
