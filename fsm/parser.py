# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    parser.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/07 14:39:30 by marvin            #+#    #+#              #
#    Updated: 2026/05/07 14:39:30 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from fsm.fsm import State, FSMContext

def	parse_answer(user_input: str):
	options = {
		"booster": "booster",
		"special": "special",
		"deck": "deck",
		"other": "other"
	}
	return (options.get(user_input))

def parse_main_category(fsm: FSMContext):
	mapping = {
		"booster": "booster",
		"boosters": "booster",
		"special": "special",
		"specials": "special",
		"deck": "deck",
		"decks": "deck",
		"other": "other"
	}
	fsm.main_category = mapping.get(fsm.answer)
	fsm.data["category"] = fsm.main_category
	fsm.current_state = State.SELECT_SUBCATEGORY
	return (fsm.current_state)

def	parse_sub_category(fsm: FSMContext, options: list):
	for i, option in enumerate(options):
		print(str(i) + ": ", option)
	while (True):
		try:
			answer = int(input("> "))
			if (answer < 0 or answer >= len(options)):
				print("Invalid Token")
				continue
			break
		except ValueError:
			print("Please enter a valid number")
	fsm.subcategory = options[answer]
	fsm.data["subcategory"] = fsm.subcategory
	fsm.current_state = State.BUILD_QUERY
	return (fsm.current_state)

def	main_dispatcher(fsm: FSMContext):
	prefix = {
		"other": "List of "
	}
	return (prefix.get(
		fsm.main_category,
		"List of Cardfight!! Vanguard "
	))

def sub_dispatcher(fsm: FSMContext):
	sub_dispatch = {
		"Unique Booster Sets": fsm.subcategory,
		"Monthly Bushiroad": fsm.subcategory
	}
	if (fsm.subcategory in sub_dispatch):
		return (sub_dispatch[fsm.subcategory])

def dispatcher(fsm: FSMContext):

	result = sub_dispatcher(fsm)

	if (result is not None):
		return (result)

	return (
		main_dispatcher(fsm)
		+ fsm.subcategory
	)
