# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by kjroy93           #+#    #+#              #
#    Updated: 2026/08/14 16:09:35 by kmarrero         ###   ########.fr        #
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

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt):
		print("Program Close")
