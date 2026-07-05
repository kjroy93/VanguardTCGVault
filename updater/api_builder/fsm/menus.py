# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    menus.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/07 14:39:27 by marvin            #+#    #+#              #
#    Updated: 2026/05/07 14:39:27 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from api_builder.fsm.states		import State
from api_builder.fsm.fsm		import FSMContext
from api_builder.fsm.constants	import CATEGORIES
from api_builder.fsm.url_parser	import parse_answer, parse_main_category, parse_sub_category

def entry_point(fsm: FSMContext):

	def start_message():
		print("Welcome to VanguardTCGScrapper")
		print("\n")
		print("What info do you need from the website?")

	start_message()
	answer = None
	while (answer is None):
		for index, key in enumerate(CATEGORIES):
			print(index, ":", key)
		user_input = int(input("> ").lower())
		answer = parse_answer(user_input)
		if (answer is None):
			print("Invalid option. Try again")
	print("You selected:", answer)
	fsm.answer = answer
	fsm.data["answer"] = fsm.answer
	fsm.current_state = State.SELECT_MAIN_CATEGORY
	return (fsm.current_state)

def	select_category(fsm: FSMContext):
	return (parse_main_category(fsm))

def	select_subcategory(fsm: FSMContext):
	options = CATEGORIES.get(fsm.main_category)
	if (options is None):
		print("There is no subcategory for this query." \
		"Please, check out dictionary CATEGORIES")
		fsm.current_state = State.ERROR
		return (fsm.current_state)

	print("Which subcategory you want to scrap?")
	print("indentify it with the index number:\n")
	return (parse_sub_category(fsm, options))
