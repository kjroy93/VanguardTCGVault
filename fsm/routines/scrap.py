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
import asyncio
import random
import pandas as pd
from fsm.routines.check_data_base import build_set_path
from data.vanguard_data import VanguardStorage
from parsers.vanguard_parser import VanguardParser
from classifier.vanguard_classifier import VanguardClassifier
from api_builder.vanguard_api_build import VanguardScrapper
from api_builder.api_request import header

async def	main_scrap_routine(parser: VanguardParser,
					   		storage: VanguardStorage,
							scrapper: VanguardScrapper,
							classifier: VanguardClassifier):
	for block in ["LB", "LL", "G", "V", "D", "DZ"]:
		consult = parser.make_consults(getattr(storage, block.lower()))
		for tpl in consult.values():
			n = random.randint(1, 10)
			await asyncio.sleep(n)
			api_result = await scrapper.api.get(
				params=tpl,
				headers=header
			)
			wikitex = scrapper.obtain_wikitex(api_result)
			data = scrapper.make_cardlist_from_str(wikitex=wikitex)
			infobox = parser.infobox(wikitex)
			is_d = False
			is_deck = False
			if (block in ["D", "DZ"]):
				is_d = True
			rows = storage.prepare_data(data, 6, is_d=is_d, is_deck=is_deck, infobox=infobox)
			df = pd.DataFrame(rows, columns=[
				"CardNo", "Name", "Grade", "Faction",
				"FactionType", "Type", "Rarity", "Release"
			])
			set_number = classifier.obtain_set_number(
				data[0]
			)
			path = build_set_path(
				category="boosters",
				set_type="main",
				block=block,
				set_number=set_number
			)
			path.parent.mkdir(
				parents=True,
				exist_ok=True
			)
			df.to_parquet(path)
