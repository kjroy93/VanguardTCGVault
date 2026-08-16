# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    transitions.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/16 17:35:52 by kjroydev          #+#    #+#              #
#    Updated: 2026/08/16 17:38:41 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from routine.vanguard_routine	import VanguardRoutine
from routine.fsm				import StateMachine, PipelineState, PipelineEvent

def	add_transitions_to_state_machine(sm: StateMachine):
	sm.add_transition(
		PipelineState.ENTRY_POINT,
		PipelineEvent.SELECT_CATEGORY,
		PipelineState.MAIN_CATEGORY_SELECTED,
		VanguardRoutine.select_category,
	)

	sm.add_transition(
		PipelineState.MAIN_CATEGORY_SELECTED,
		PipelineEvent.SELECT_SUBCATEGORY,
		PipelineState.SUB_CATEGORY_SELECTED,
		VanguardRoutine.select_subcategory
	)

	sm.add_transition(
		PipelineState.SUB_CATEGORY_SELECTED,
		PipelineEvent.BUILD_QUERY,
		PipelineState.QUERY_BUILT,
		VanguardRoutine.make_query
	)

	sm.add_transition(
		PipelineState.QUERY_BUILT,
		PipelineEvent.MAKE_CONSULT,
		PipelineState.SET_CONSULT,
		VanguardRoutine.set_api_consult
	)

	sm.add_transition(
		PipelineState.SET_CONSULT,
		PipelineEvent.CLEAN_RESULT,
		PipelineState.URL_PARSED,
		VanguardRoutine.parse_links
	)

	sm.add_transition(
		PipelineState.URL_PARSED,
		PipelineEvent.MAIN_ROUTINE,
		PipelineState.DONE,
		VanguardRoutine.main_scrap_routine
	)

	sm.add_transition(
		PipelineState.DONE,
		PipelineEvent.ASK_IF_CONTINUE,
		PipelineState.ENTRY_POINT,
		VanguardRoutine.ask_user
	)
