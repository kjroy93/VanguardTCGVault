# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    actions.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/08 20:17:07 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/09 21:14:13 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from wiki_api.vanguard_api_build				import header
from utils.constants							import CATEGORIES
from utils.utils								import smart_sleep
from utils.utils 								import construct_rules
from pipeline.builder							import VanguardPipeline
from fsm										import ParseContext as Context

def	select_category():
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
	Context.category = answer
	Context.column = dispatcher[answer]

def	select_subcategory():
	options = CATEGORIES.get(Context.category)
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
	Context.subcategory = options[answer]

def	make_query():
	def __dispatcher():
		def	main_dispatcher():
			prefix = {
				"other": "List of "
			}
			return (prefix.get(
				Context.category,
				"List of Cardfight!! Vanguard "
			))

		def sub_dispatcher():
			sub_dispatch = {
				"Unique Booster Sets": Context.subcategory,
				"Monthly Bushiroad": Context.subcategory
			}
			if (Context.subcategory in sub_dispatch):
				return (sub_dispatch[Context.subcategory])

		result = sub_dispatcher()

		if (result is not None):
			return (result)

		return (
			main_dispatcher()
			+ Context.subcategory
		)

	prefix = __dispatcher()
	if (prefix is None):
		raise ValueError("No element selected in query dispatcher")
	param = {
		"action": "parse",
		"page": f"{prefix}",
		"format": "json"
	}
	Context.query_page = prefix
	Context.query_parameters = param

async def	set_api_consult(pipeline: VanguardPipeline):
	rules = construct_rules(
		Context.data["page"].split()[4]
	)
	await smart_sleep()
	pipeline.classifier._define_rules(rules)
	param = Context.data["param"]
	response = await pipeline.scrapper.api.get(
		param,
		header
	)
	error = response.get("Error")
	if (error is not None):
		raise RuntimeError(f"Wiki API returned error: {response}")
	Context.response = response

async def	routine(card_fsm: CardFSM, pipeline: VanguardPipeline):
	for block in ["LB", "LL", "G", "V", "D", "DZ"]:
		consult = pipeline.scrapper.api.make_consults(getattr(pipeline.storage, block.lower()), "consult")
		for tpl in consult.values():
			card_fsm.fsm_context.data["tpl"] = tpl
			await make_api_calls(card_fsm, pipeline)
			parser(card_fsm, pipeline)
			if (block in ["D", "DZ"]):
				card_fsm.context.is_d = True
			card_fsm.state = ParserState.START
			try:
				rows = pipeline.storage.prepare_data(card_fsm.fsm_context.data["crude_cards"], card_fsm)
			except (KeyError, ValueError, AttributeError):
				state = State.ERROR
				return (state)
			columns = column_dispatcher(card_fsm)
			df = pd.DataFrame(rows, columns=columns)
			set_number = pipeline.classifier.obtain_set_number(
				card_fsm.fsm_context.data["crude_cards"][0]
			)
			path = build_set_path(
				category=card_fsm.fsm_context.data["answer"],
				set_type=card_fsm.fsm_context.data["subcategory"].strip().lower().split()[0],
				block=block,
				set_number=set_number
			)
			path.parent.mkdir(
				parents=True,
				exist_ok=True
			)
			path = get_duplicate_path(path)
			df.to_parquet(path)
			print(df)

def	check_url():
	pass