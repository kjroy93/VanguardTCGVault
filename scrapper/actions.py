# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    actions.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/08 20:17:07 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/13 16:24:44 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from wiki_api.vanguard_api				import header
from utils.constants							import CATEGORIES
from pipeline.builder							import VanguardPipeline
from fsm										import ParseContext as Context
from utils.utils								import smart_sleep, construct_rules

def	select_category(ctx: Context):
	print("Welcome to VanguardTCGScrapper\n")
	print("What info do you need from the website?")

	options = {
		0: "boosters",
		1: "specials",
		2: "decks",
		3: "others",
		4: "cards"
	}

	dispatcher = {
		"boosters": "table",
		"specials": "table",
		"decks": "decks",
		"others": "",
		"cards": "cards"
	}

	for k,v in options.values():
		print(f'{k}: {v}')
	
	while (True):
		user_input = int(input("> ").strip().lower())
		if (user_input is None or user_input not in any(options.keys())):
			continue
		break
	
	answer = options.get(user_input)
	ctx.category = answer
	ctx.column = dispatcher[answer]

def	select_subcategory(ctx: Context):
	options = CATEGORIES.get(ctx.category)
	for i, option in enumerate(options):
		print(f'{i}: {option}')
	while (True):
		try:
			answer = int(input("> ").strip().lower())
			if (answer < 0 or answer >= len(options)):
				print("Invalid Token")
				continue
			break
		except ValueError as e:
			print("Please enter a valid number")
	ctx.subcategory = options[answer]

def	make_query(ctx: Context):
	def __dispatcher():
		def	main_dispatcher() -> str | None:
			prefix = {
				"other": "List of "
			}
			return (prefix.get(
				ctx.category,
				"List of Cardfight!! Vanguard "
			))

		def sub_dispatcher() -> str | None:
			sub_dispatch = {
				"Unique Booster Sets": ctx.subcategory,
				"Monthly Bushiroad": ctx.subcategory
			}
			if (ctx.subcategory in sub_dispatch):
				return (sub_dispatch[ctx.subcategory])

		result = sub_dispatcher()

		if (result is not None):
			return (result)

		return (
			main_dispatcher()
			+ ctx.subcategory
		)

	prefix = __dispatcher()
	if (prefix is None):
		raise ValueError("No element selected in query dispatcher")
	param = {
		"action": "parse",
		"page": f"{prefix}",
		"format": "json"
	}
	ctx.query_page = prefix
	ctx.query_parameters = param

def	check_url():
	pass