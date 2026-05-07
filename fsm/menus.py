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

from fsm.fsm		import State, FSMContext
from fsm			import parser

CATEGORIES = {
	"booster": [
		"Booster Sets",
		"Extra Booster Sets",
		"Character Booster Sets",
		"Combinations Booster Sets",
		"Clan Booster Sets",
		"Title Booster Sets",
		"Unique Booster Sets",
	],
	"special": [
		"Fighters Collections",
		"Revival Collections",
		"Collector's Sets",
		"Special Series"
	],
	"deck": [
		"Trial Decks",
		"Legend Decks",
		"Character Decks",
		"Half Decks",
		"Premiun Fighter Decks",
		"Structure Decks"
	],
	"other": [
		"Promo Cards",
		"V Promo Cards",
		"Monthly Bushiroad Cards"
	]
}

def entry_point(fsm: FSMContext):

	def start_message():
		print("Welcome to VanguardTCGScrapper")
		print("What info do you need from the website?")
		print("booster")
		print("special")
		print("deck")
		print("other")

	start_message()
	answer = None
	while (answer is None):
		user_input = input("> ").lower()
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

def	make_query(fsm: FSMContext):

	def	dispatcher(main_cateogry: str):
		prefix = {
			"other": "List of "
		}
		return (prefix.get(
			main_cateogry,
			"List of Cardfight!! Vanguard"
		))

	prefix = dispatcher(fsm.main_category)
	param = {
		"action": "parse",
		"page": prefix + " " + fsm.subcategory,
		"format": "json"
	}
	fsm.data["param"] = param
	fsm.current_state = State.FETCH
	return (fsm.current_state)