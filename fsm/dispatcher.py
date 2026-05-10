# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dispatcher.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 11:12:10 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 11:12:10 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from fsm.fsm import FSMContext

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
