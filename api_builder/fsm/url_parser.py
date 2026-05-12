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
from api_builder.fsm.states	import State
from api_builder.fsm.fsm	import FSMContext

def	parse_answer(user_input: str):
	options = {
		0: "boosters",
		1: "specials",
		2: "decks",
		3: "others"
	}
	return (options.get(user_input))

def parse_main_category(fsm: FSMContext):
	fsm.main_category = fsm.answer
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

