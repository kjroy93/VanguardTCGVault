# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    query_builder.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 11:14:39 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 11:14:39 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from api_builder.fsm.states import State
from api_builder.fsm.fsm import FSMContext

def	__main_dispatcher(fsm: FSMContext):
	prefix = {
		"other": "List of "
	}
	return (prefix.get(
		fsm.main_category,
		"List of Cardfight!! Vanguard "
	))

def __sub_dispatcher(fsm: FSMContext):
	sub_dispatch = {
		"Unique Booster Sets": fsm.subcategory,
		"Monthly Bushiroad": fsm.subcategory
	}
	if (fsm.subcategory in sub_dispatch):
		return (sub_dispatch[fsm.subcategory])

def dispatcher(fsm: FSMContext):
	result = __sub_dispatcher(fsm)

	if (result is not None):
		return (result)

	return (
		__main_dispatcher(fsm)
		+ fsm.subcategory
	)

def	make_query(fsm: FSMContext):
	prefix = dispatcher(fsm)
	if (prefix is None):
		fsm.current_state = State.END
		return (fsm.current_state)
	param = {
		"action": "parse",
		"page": f"{prefix}",
		"format": "json"
	}
	fsm.data["param"] = param
	fsm.data["page"] = prefix
	fsm.current_state = State.FETCH
	return (fsm.current_state)
