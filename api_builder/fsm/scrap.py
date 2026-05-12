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
from api_builder.api_request		import header
from api_builder.fsm.fsm			import FSMContext
from data.check_data_base			import build_set_path
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from api_builder.vanguard_api_build	import VanguardScrapper
from classifier.vanguard_classifier	import VanguardClassifier

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

async def	main_scrap_routine(parser: VanguardParser,
					   		storage: VanguardStorage,
							scrapper: VanguardScrapper,
							classifier: VanguardClassifier,
							fsm: FSMContext):
	for block in ["LB", "LL", "G", "V", "D", "DZ"]:
		consult = parser.make_consults(getattr(storage, block.lower()), "consult")
		for tpl in consult.values():
			n = random.randint(5, 10)
			await asyncio.sleep(n)
			api_result = await scrapper.api.get(
				params=tpl,
				headers=header
			)
			wikitex = scrapper.obtain_wikitex(api_result)
			crude_cards = scrapper.make_cardlist_from_str(wikitex=wikitex)
			infobox = parser.infobox(wikitex)
			is_d = False
			is_deck = False
			if (block in ["D", "DZ"]):
				is_d = True
			rows = storage.prepare_data(crude_cards, 6, is_d=is_d, is_deck=is_deck, infobox=infobox)
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
				set_type=fsm.subcategory.strip().lower().split()[0],
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