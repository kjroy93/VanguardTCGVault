# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by kjroy93           #+#    #+#              #
#    Updated: 2026/08/16 17:40:34 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import asyncio

# Library
from utils.constants				import EVENTS
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from pipeline.builder				import VanguardPipeline
from classifier.vanguard_classifier	import VanguardClassifier
from wiki_api.vanguard_api			import MediaWikiAPI, VanguardScrapper
from routine.transitions			import add_transitions_to_state_machine
from routine.fsm					import StateMachine, PipelineState, SetContext, PipelineEvent
# from cards.fsm						import CardStateMachine, CardState, CardContext, CardEvent

scrapper_sm: StateMachine[PipelineState, PipelineEvent, SetContext, VanguardPipeline] = StateMachine(PipelineState.ENTRY_POINT)
# card_sm: CardStateMachine[CardState, CardEvent, CardContext] = CardStateMachine()

add_transitions_to_state_machine(scrapper_sm)

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
			for event in EVENTS:
				print(f" --> state machine current state: {scrapper_sm.current_state.name}\n", end="")
				print(f" --> next event: {(event.name)}\n", end="")
				await scrapper_sm.handle(
					context,
					event,
					pipeline
				)
			await scrapper_sm.handle(
				context,
				PipelineEvent.ASK_IF_CONTINUE,
				scrapper_sm
			)
			if (scrapper_sm.current_state == PipelineState.FINISH):
				break
	finally:
		await pipeline.scrapper.api.close_session()
		print("Session Closed")

if (__name__ == "__main__"):
	try:
		asyncio.run(main())
	except (KeyboardInterrupt):
		print("Program Close")
