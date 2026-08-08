# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    transitions.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/08 20:17:07 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/08 20:28:06 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from utils.constants							import CATEGORIES
from api_builder.fsm.fsm						import ParseContext as Context
from api_builder.api_constructor					import header
from utils.utils								import smart_sleep
from utils.utils 								import construct_rules
from pipeline.builder							import VanguardPipeline

def	select_category():
	print("Welcome to VanguardTCGScrapper\n")
	print("What info do you need from the website?")
	while (1):
		user_input = int(input("> ").lower())
		if (user_input is None):
			continue
		break

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
	
	answer = options.get(user_input)
	Context.category = answer
	Context.column = dispatcher[answer]

def	select_subcategory():
	options = CATEGORIES.get(Context.category)
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
	Context.subcategory = options[answer]

def	make_query(fsm: Context):
	def __dispatcher(fsm: Context):
		def	main_dispatcher(fsm: Context):
			prefix = {
				"other": "List of "
			}
			return (prefix.get(
				fsm.category,
				"List of Cardfight!! Vanguard "
			))

		def sub_dispatcher(fsm: Context):
			sub_dispatch = {
				"Unique Booster Sets": fsm.subcategory,
				"Monthly Bushiroad": fsm.subcategory
			}
			if (fsm.subcategory in sub_dispatch):
				return (sub_dispatch[fsm.subcategory])

		result = sub_dispatcher(fsm)

		if (result is not None):
			return (result)

		return (
			main_dispatcher(fsm)
			+ fsm.subcategory
		)

	prefix = __dispatcher(fsm)
	if (prefix is None):
		raise ValueError("No element selected in query dispatcher")
	param = {
		"action": "parse",
		"page": f"{prefix}",
		"format": "json"
	}
	fsm.query_page = prefix
	fsm.query_parameters = param

async def	api_consult(fsm: Context, pipeline: VanguardPipeline):
	rules = construct_rules(
		fsm.data["page"].split()[4]
	)
	await smart_sleep()
	pipeline.classifier._define_rules(rules)
	param = fsm.data["param"]
	response = await pipeline.scrapper.api.get(
		param,
		header
	)
	error = response.get("Error")
	if (error is not None):
		raise RuntimeError(f"Wiki API returned error: {response}")


def	check_url():
	pass