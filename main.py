# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by kjroy93           #+#    #+#              #
#    Updated: 2026/08/13 19:47:10 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import asyncio

# Library
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from pipeline.builder				import VanguardPipeline
from classifier.vanguard_classifier	import VanguardClassifier
from wiki_api.vanguard_api			import MediaWikiAPI, VanguardScrapper
from scrapper.vanguard_routine		import VanguardRoutine
from scrapper.fsm					import StateMachine, ParseState, ParseContext, ParseEvent
# from cards.fsm						import CardStateMachine, CardState, CardContext, CardEvent

scrapper_sm: StateMachine[ParseState, ParseEvent, ParseContext, VanguardPipeline] = StateMachine(ParseState.ENTRY_POINT)
# card_sm: CardStateMachine[CardState, CardEvent, CardContext] = CardStateMachine()

scrapper_sm.add_transition(
	ParseState.ENTRY_POINT,
	ParseEvent.SELECT_CATEGORY,
	ParseState.MAIN_CATEGORY_SELECTED,
	VanguardRoutine.select_category,
)

scrapper_sm.add_transition(
	ParseState.MAIN_CATEGORY_SELECTED,
	ParseEvent.SELECT_SUBCATEGORY,
	ParseState.SUB_CATEGORY_SELECTED,
	VanguardRoutine.select_subcategory
)

scrapper_sm.add_transition(
	ParseState.SUB_CATEGORY_SELECTED,
	ParseEvent.BUILD_QUERY,
	ParseState.QUERY_BUILT,
	VanguardRoutine.make_query
)

scrapper_sm.add_transition(
	ParseState.QUERY_BUILT,
	ParseEvent.MAKE_CONSULT,
	ParseState.SET_CONSULT,
	VanguardRoutine.set_api_consult
)

scrapper_sm.add_transition(
	ParseState.SET_CONSULT,
	ParseEvent.CLEAN_RESULT,
	ParseState.URL_PARSED,
	VanguardRoutine.parse_links
)

scrapper_sm.add_transition(
	ParseState.URL_PARSED,
	ParseEvent.MAIN_ROUTINE,
	ParseState.END,
	VanguardRoutine.main_scrap_routine
)

events = [
    ParseEvent.SELECT_CATEGORY,
    ParseEvent.SELECT_SUBCATEGORY,
    ParseEvent.BUILD_QUERY,
    ParseEvent.MAKE_CONSULT,
    ParseEvent.CLEAN_RESULT,
    ParseEvent.MAIN_ROUTINE,
]

async def main():
	web = MediaWikiAPI()
	pipeline = VanguardPipeline(
		VanguardParser(),
		VanguardStorage(),
		VanguardScrapper(web),
		VanguardClassifier()
	)
	context = ParseContext()
	await pipeline.scrapper.api.init_session()
	try:
		for event in events:
			print(f"{scrapper_sm.current_state.name}")
			print(f"-- {(event.name)} -->",
		 		end="")
			await scrapper_sm.handle(
				context,
				event,
				pipeline
			)
	finally:
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
	try:
		asyncio.run(main())
	except (KeyboardInterrupt):
		print("Program Close")
