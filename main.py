# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 16:07:31 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import asyncio

# Library
from api_builder.fsm				import fsm
from api_builder.fsm				import menus
from api_builder.fsm.states			import State
from api_builder.fsm				import scrap
from cards.fsm						import CardFSM
from api_builder.fsm.query_builder	import make_query
from api_builder.fsm.url_parser		import parse_links
from api_builder.fsm.fetch			import fetch_routine
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from pipeline.builder				import VanguardPipeline
from classifier.vanguard_classifier	import VanguardClassifier
from api_builder.vanguard_api_build	import MediaWikiAPI, VanguardScrapper

async def main():
	web = MediaWikiAPI()
	pipeline = VanguardPipeline(
		VanguardParser(),
		VanguardStorage(),
		VanguardScrapper(web),
		VanguardClassifier()
	)
	await pipeline.scrapper.api.init_session()
	state_machine = fsm.FSMContext()
	state = State.ENTRY_POINT

	while (state != State.END):
		if (state == State.ENTRY_POINT):
			state = menus.entry_point(state_machine)
		elif (state == State.SELECT_MAIN_CATEGORY):
			state = menus.select_category(state_machine)
		elif (state == State.SELECT_SUBCATEGORY):
			state = menus.select_subcategory(state_machine)
		elif (state == State.BUILD_QUERY):
			state = make_query(state_machine)
		elif (state == State.FETCH):
			state = await fetch_routine(state_machine, pipeline)
		elif (state == State.PARSE):
			state = parse_links(state_machine, pipeline)
		elif (state == State.SCRAP):
			card_fsm = CardFSM(state_machine)
			await scrap.main_scrap_routine(card_fsm, pipeline)
			print("Do you wish to continue the scrap process? [y]es | [n]o")
			answer = input("> ").strip().lower()
			if (answer in ("y", "yes")):
				state = State.ENTRY_POINT
			elif (answer in ("n", "no")):
				state = State.END
	await pipeline.scrapper.api.close_session()

# async def main():
# 	web = MediaWikiAPI()
# 	pipeline = VanguardPipeline(
# 		VanguardScrapper(web),
# 		VanguardParser(),
# 		VanguardClassifier(),
# 		VanguardStorage()
# 	)
# 	await pipeline.scrapper.api.init_session()
# 	state_machine = fsm.FSMContext()
# 	state = State.ENTRY_POINT
# 	while (state != State.END):
# 		if (state == State.ENTRY_POINT):
# 			state = menus.entry_point(state_machine)
# 		elif (state == State.SELECT_MAIN_CATEGORY):
# 			state = menus.select_category(state_machine)
# 		elif (state == State.SELECT_SUBCATEGORY):
# 			state = menus.select_subcategory(state_machine)
# 		elif (state == State.BUILD_QUERY):
# 			state = make_query(state_machine)
# 		elif (state == State.FETCH):
# 			state = await fetch_routine(state_machine, pipeline.scrapper)
# 		elif (state == State.PARSE):
# 			pipeline.classifier._define_rules(construct_rules(state_machine.main_category.capitalize()))
# 			state = parse_links(
# 				state_machine, pipeline.parser, pipeline.storage,
# 				pipeline.scrapper, pipeline.classifier
# 			)
# 			dz_consults = pipeline.parser.make_consults(pipeline.storage.g)
# 			api_answer = await pipeline.scrapper.api.get(params=dz_consults[13], headers=header)
# 			wikitex = pipeline.scrapper.obtain_wikitex(api_answer)
# 			data = pipeline.scrapper.make_cardlist_from_str(wikitex=wikitex)
# 			infobox = pipeline.parser.infobox(wikitex)
# 			data = pipeline.storage.prepare_data([data[2]], 6, infobox=infobox)

if __name__ == "__main__":
	asyncio.run(main())
