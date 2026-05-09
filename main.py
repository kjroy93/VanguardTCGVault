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
from fsm import	fsm, menus
from fsm.states import State
from fsm.routines import scrap
from utils.utils import construct_rules
from fsm.routines.parse import parse_links
from fsm.routines.fetch import fetch_routine
from pipeline.query_builder import make_query
from pipeline.builder import VanguardPipeline
from data.vanguard_data import VanguardStorage
from parsers.vanguard_parser import VanguardParser
from classifier.vanguard_classifier import VanguardClassifier
from api_builder.vanguard_api_build import MediaWikiAPI, VanguardScrapper

async def main():
	web = MediaWikiAPI()
	pipeline = VanguardPipeline(
		VanguardScrapper(web),
		VanguardParser(),
		VanguardClassifier(),
		VanguardStorage()
	)
	await pipeline.scrapper.api.init_session()
	state_machine = fsm.FSMContext()
	state = State.ENTRY_POINT

	while state != State.END:
		if state == State.ENTRY_POINT:
			state = menus.entry_point(state_machine)
		elif state == State.SELECT_MAIN_CATEGORY:
			state = menus.select_category(state_machine)
		elif state == State.SELECT_SUBCATEGORY:
			state = menus.select_subcategory(state_machine)
		elif state == State.BUILD_QUERY:
			state = make_query(state_machine)
		elif state == State.FETCH:
			rules = construct_rules(
				state_machine.data["page"].split()[4]
			)
			pipeline.classifier._define_rules(rules)
			state = await fetch_routine(
				state_machine,
				pipeline.scrapper
			)
		elif state == State.PARSE:
			pipeline.classifier._define_rules(construct_rules(state_machine.main_category.capitalize()))
			state = parse_links(
				state_machine, pipeline.parser, pipeline.storage,
				pipeline.scrapper, pipeline.classifier
			)
			await scrap.main_scrap_routine(pipeline.parser, pipeline.storage, pipeline.scrapper, pipeline.classifier, state_machine)
			print("Do you wish to continue the scrap process? [y]es | [n]o")
			answer = input("> ").strip().lower()
			if (answer in ("y", "yes")):
				state = State.ENTRY_POINT
			elif (answer in ("n", "no")):
				state = State.END
	await pipeline.scrapper.api.close_session()

if __name__ == "__main__":
	asyncio.run(main())
