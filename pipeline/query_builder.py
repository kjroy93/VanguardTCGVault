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

from fsm.fsm import FSMContext
from fsm.states import State
from fsm.dispatcher import dispatcher

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
