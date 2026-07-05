# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    fetch.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 11:01:22 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 11:01:22 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from api_builder.fsm.states						import State
from api_builder.api_request					import header
from api_builder.fsm.fsm						import FSMContext
from utils.utils								import smart_sleep
from utils.utils 								import construct_rules
from pipeline.builder							import VanguardPipeline

async def	fetch_routine(fsm: FSMContext, pipeline: VanguardPipeline):
	rules = construct_rules(
		fsm.data["page"].split()[4]
	)
	await smart_sleep()
	pipeline.classifier._define_rules(rules)
	param = fsm.data["param"]
	response = await pipeline.scrapper.api.get(
		param,
		header
	)
	error = response.get("Error")
	if (error is not None):
		raise RuntimeError(f"Wiki API returned error: {response}")
	fsm.data["response"] = response
	fsm.current_state = State.PARSE
	return (fsm.current_state)
