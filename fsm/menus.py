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
from fsm.states	import State
from fsm		import parser
from fsm.fsm	import FSMContext

CATEGORIES = {
	"boosters": [
		"Booster Sets",
		"Extra Booster Sets",
		"Character Booster Sets",
		"Clan Booster Sets",
		"Title Booster Sets",
		"Unique Booster Sets",
	],
	"specials": [
		"Fighters Collections",
		"Revival Collections",
		"Collector's Sets",
		"Special Series"
	],
	"decks": [
		"Trial Decks",
		"Legend Decks",
		"Character Decks",
		"Half Decks",
		"Premiun Fighter Decks",
		"Structure Decks"
	],
	"others": [
		"Promo Cards",
		"V Promo Cards",
		"Monthly Bushiroad Cards"
	]
}

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
		answer = parser.parse_answer(user_input)
		if (answer is None):
			print("Invalid option. Try again")
	print("You selected:", answer)
	fsm.answer = answer
	fsm.data["answer"] = fsm.answer
	fsm.current_state = State.SELECT_MAIN_CATEGORY
	return (fsm.current_state)

def	select_category(fsm: FSMContext):
	return (parser.parse_main_category(fsm))

def	select_subcategory(fsm: FSMContext):
	options = CATEGORIES.get(fsm.main_category)
	if (options is None):
		print("There is no subcategory for this query." \
		"Please, check out dictionary CATEGORIES")
		fsm.current_state = State.ERROR
		return (fsm.current_state)

	print("Which subcategory you want to scrap?")
	print("indentify it with the index number:\n")
	return (parser.parse_sub_category(fsm, options))
