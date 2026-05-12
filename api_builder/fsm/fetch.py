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

# Import
import asyncio

# Library
from api_builder.fsm.states						import State
from api_builder.api_request					import header
from api_builder.fsm.fsm						import FSMContext
from api_builder.vanguard_api_build				import VanguardScrapper

async def	fetch_routine(fsm: FSMContext, scrapper: VanguardScrapper):
	param = fsm.data["param"]
	response = await scrapper.api.get(
		param,
		header
	)
	error = response.get("Error")
	if (error is not None):
		raise RuntimeError(f"Wiki API returned error: {response}")
	fsm.data["response"] = response
	fsm.current_state = State.PARSE
	return (fsm.current_state)
