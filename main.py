# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by kjroy93           #+#    #+#              #
#    Updated: 2026/08/15 18:56:35 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import asyncio

# Library
from parsers.vanguard_parser		import VanguardParser
from routine.vanguard_routine		import VanguardRoutine
from data.vanguard_data				import VanguardStorage
from pipeline.builder				import VanguardPipeline
from classifier.vanguard_classifier	import VanguardClassifier
from wiki_api.vanguard_api			import MediaWikiAPI, VanguardScrapper
from routine.fsm					import StateMachine, PipelineState, SetContext, PipelineEvent
# from cards.fsm						import CardStateMachine, CardState, CardContext, CardEvent

scrapper_sm: StateMachine[PipelineState, PipelineEvent, SetContext, VanguardPipeline] = StateMachine(PipelineState.ENTRY_POINT)
# card_sm: CardStateMachine[CardState, CardEvent, CardContext] = CardStateMachine()

scrapper_sm.add_transition(
	PipelineState.ENTRY_POINT,
	PipelineEvent.SELECT_CATEGORY,
	PipelineState.MAIN_CATEGORY_SELECTED,
	VanguardRoutine.select_category,
)

scrapper_sm.add_transition(
	PipelineState.MAIN_CATEGORY_SELECTED,
	PipelineEvent.SELECT_SUBCATEGORY,
	PipelineState.SUB_CATEGORY_SELECTED,
	VanguardRoutine.select_subcategory
)

scrapper_sm.add_transition(
	PipelineState.SUB_CATEGORY_SELECTED,
	PipelineEvent.BUILD_QUERY,
	PipelineState.QUERY_BUILT,
	VanguardRoutine.make_query
)

scrapper_sm.add_transition(
	PipelineState.QUERY_BUILT,
	PipelineEvent.MAKE_CONSULT,
	PipelineState.SET_CONSULT,
	VanguardRoutine.set_api_consult
)

scrapper_sm.add_transition(
	PipelineState.SET_CONSULT,
	PipelineEvent.CLEAN_RESULT,
	PipelineState.URL_PARSED,
	VanguardRoutine.parse_links
)

scrapper_sm.add_transition(
	PipelineState.URL_PARSED,
	PipelineEvent.MAIN_ROUTINE,
	PipelineState.DONE,
	VanguardRoutine.main_scrap_routine
)

scrapper_sm.add_transition(
	PipelineState.DONE,
	PipelineEvent.ASK_IF_CONTINUE,
	PipelineState.ENTRY_POINT,
	VanguardRoutine.ask_user
)

events = [
    PipelineEvent.SELECT_CATEGORY,
    PipelineEvent.SELECT_SUBCATEGORY,
    PipelineEvent.BUILD_QUERY,
    PipelineEvent.MAKE_CONSULT,
    PipelineEvent.CLEAN_RESULT,
    PipelineEvent.MAIN_ROUTINE
]

async def main():
	web = MediaWikiAPI()
	pipeline = VanguardPipeline(
		VanguardParser(),
		VanguardStorage(),
		VanguardScrapper(web),
		VanguardClassifier()
	)
	context = SetContext()
	await pipeline.scrapper.api.init_session()
	try:
		while (True):
			for event in events:
				print(f" --> state machine current state: {scrapper_sm.current_state.name}\n", end="")
				print(f" --> next event: {(event.name)}\n", end="")
				await scrapper_sm.handle(
					context,
					event,
					pipeline
				)
			scrapper_sm.handle(
				context,
				PipelineEvent.ASK_IF_CONTINUE,
				scrapper_sm
			)
			if (scrapper_sm.current_state == PipelineState.FINISH):
				break
	finally:
		await pipeline.scrapper.api.close_session()

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt):
		print("Program Close")
