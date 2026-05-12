# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    scrap.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 20:09:12 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 20:09:12 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import random
import asyncio
from pathlib						import Path

# Dependencies
import pandas 						as pd

# Library
from utils.utils					import smart_sleep
from api_builder.api_request		import header
from data.check_data_base			import build_set_path
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from api_builder.vanguard_api_build	import VanguardScrapper
from classifier.vanguard_classifier	import VanguardClassifier
from mwparserfromhell.wikicode import Wikicode
from cards.fsm import CardFSM
from utils.utils import remove_from_list

def	get_duplicate_path(path: Path) -> Path:
	if not path.exists():
		return path
	
	stem = path.stem
	suffix = path.suffix
	parent = path.parent
	i = 1
	while True:
		new_path = parent / f"{stem}_{i}{suffix}"
		if not new_path.exists():
			return new_path
		i += 1

def	define_param(tpl: dict):
	links = {
		"action": "parse",
		"page": tpl.get("titles"),
		"prop": "links",
		"format": "json"
	}
	return (links)

async def	main_scrap_routine(parser: VanguardParser,
					   		storage: VanguardStorage,
							scrapper: VanguardScrapper,
							classifier: VanguardClassifier,
							card_fsm: CardFSM):
	for block in ["LB", "LL", "G", "V", "D", "DZ"]:
		consult = parser.make_consults(getattr(storage, block.lower()), "consult")
		for tpl in consult.values():
			link_param = define_param(tpl)
			n = smart_sleep()
			await asyncio.sleep(n)
			api_result = await scrapper.api.get(
				params=tpl,
				headers=header
			)
			n = smart_sleep()
			await asyncio.sleep(n)
			link_result = await scrapper.api.get(
				params=link_param,
				headers=header
			)
			wikitex = scrapper.obtain_wikitex(api_result)
			crude_cards = scrapper.make_cardlist_from_str(wikitex=wikitex)
			card_fsm.context.infobox = parser.infobox(wikitex)
			all_links = scrapper.obtain_links(link_result)
			parser.clean_trash_from_set(card_fsm.fsm_context.data["page"], all_links, 4, reverse=True)
			card_fsm.context.links = parser.sort_unique_url(crude_cards, all_links)
			if (block in ["D", "DZ"]):
				card_fsm.context.is_d = True
			rows = storage.prepare_data(crude_cards, card_fsm)
			df = pd.DataFrame(rows, columns=[
				"CardNo", "Name", "Grade", "Faction",
				"FactionType", "Type", "Rarity", "Release"
			])
			print(crude_cards)
			set_number = classifier.obtain_set_number(
				crude_cards[0]
			)
			path = build_set_path(
				category="boosters",
				set_type=card_fsm.fsm_context.subcategory.strip().lower().split()[0],
				block=block,
				set_number=set_number
			)
			path.parent.mkdir(
				parents=True,
				exist_ok=True
			)
			path = get_duplicate_path(path)
			df.to_parquet(path)
			print(df)