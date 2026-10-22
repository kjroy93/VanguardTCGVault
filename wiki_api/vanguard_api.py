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
import asyncio
from typing			import List, Union

# Dependencies
import	aiohttp
import	mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

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
		try:
			async with self.session.get(
				self.API_URL,
				params=params,
				headers=headers
			) as response:
				response.raise_for_status()
				return (await response.json())
		except (aiohttp.ClientError, asyncio.TimeoutError) as error:
			raise ValueError(f"Wiki request failed ({type(error).__name__}): {error}") from error


class	VanguardScrapper:
	def	__init__(self, api: MediaWikiAPI):
		self.api = api

	def	obtain_links(self, data: JSONType):
		page_titles = []
		for page_link in data["parse"]["links"]:
			if (page_link.get("ns") == 0):
				page_titles.append(page_link["*"])
		return (page_titles)
	
	def	obtain_wikitex(self, curl: JSONType) -> Wikicode:
		"""
		Function to obtain the content of a not parsed curl request to the MediaWikiAPI request.
		This function only work if the cards label information it's the same in this function
		('query', 'pages', 'revisions', 'slots', 'main', '*')\n
		"*" -> has cards info
		
		Parameters:
			curl: answer of the API.

		Returns:
			Parsed wikitext. Invalid API responses raise ValueError.
		"""
		if (not isinstance(curl, dict)):
			raise ValueError("Invalid Wiki API response: expected a JSON object")
		if ("error" in curl):
			raise ValueError(f"Wiki API error: {curl['error']}")
		query = curl.get("query")
		pages = query.get("pages") if isinstance(query, dict) else None
		if (not isinstance(pages, dict) or not pages):
			raise ValueError("Wiki API returned no pages")
		page = next(iter(pages.values()))
		if (not isinstance(page, dict)):
			raise ValueError("Invalid page data in Wiki API response")
		title = page.get("title", "unknown page")
		if ("missing" in page or "invalid" in page):
			raise ValueError(f"Wiki page does not exist or is invalid: {title}")
		revisions = page.get("revisions")
		if (not isinstance(revisions, list) or not revisions or not isinstance(revisions[0], dict)):
			raise ValueError(f"No revision available for page: {title}")
		slots = revisions[0].get("slots")
		main = slots.get("main") if isinstance(slots, dict) else None
		content = main.get("*") if isinstance(main, dict) else None
		if (not isinstance(content, str)):
			raise ValueError(f"No wikitext content available for page: {title}")
		return mwparserfromhell.parse(content)

	async def	api_calls(self, ctx: SetContext):

		def	define_param(tpl: dict):
			card_links_params = {
				"action": "parse",
				"page": tpl.get("titles"),
				"prop": "links",
				"format": "json"
			}
			return (card_links_params)

		card_links_params = define_param(ctx.tpl)
		await smart_sleep()
		api_result = await self.api.get(
			params=ctx.tpl,
			headers=HEADER
		)
		# Stop this set before requesting links if the page request failed.
		self.obtain_wikitex(api_result)
		await smart_sleep()
		card_links_response = await self.api.get(
			params=card_links_params,
			headers=HEADER
		)

		ctx.api_result = api_result
		ctx.card_links_response = card_links_response
