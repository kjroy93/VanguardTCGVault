# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_api.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:24:34 by marvin            #+#    #+#              #
#    Updated: 2026/08/17 03:48:47 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing			import List, Union

# Dependencies
import	aiohttp
import	mwparserfromhell

# Libraries
from routine.fsm	import SetContext
from utils.utils	import smart_sleep

# Definitions
JSONType = dict[str]
HEADER = {
	"User-Agent": "VanguardScrapper/1.104 (Python; contact: kmarrero1993@gmail.com)"
}

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
		('query', 'pages', 'revisions', 'slots', 'main', '*')\n
		"*" -> has cards info
		
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

	async def	api_calls(self, ctx: SetContext):

		def	define_param(tpl: dict):
			links = {
				"action": "parse",
				"page": tpl.get("titles"),
				"prop": "links",
				"format": "json"
			}
			return (links)

		param = define_param(ctx.tpl)
		await smart_sleep()
		api_result = await self.api.get(
			params=ctx.tpl,
			headers=HEADER
		)
		await smart_sleep()
		link_result = await self.api.get(
			params=param,
			headers=HEADER
		)

		ctx.api_result = api_result
		ctx.links = link_result
