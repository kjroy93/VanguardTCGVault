# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/13 16:07:45 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/16 20:01:57 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
import pandas						as pd

# Library
from wiki_api.vanguard_api			import HEADER
from data							import check_data_base
from pipeline.builder				import VanguardPipeline
from classifier.classifier			import process_items, sort_storage_list
from routine.fsm					import SetContext, StateMachine, PipelineState
from utils.constants				import DICT_S, CATEGORIES, VALID_DATABASES, OPTIONS
from utils.utils					import remove_from_list, smart_sleep, construct_rules, dispatcher, convert_to_int, column_dispatcher

class	VanguardRoutine:
	@staticmethod
	def	select_category(set_ctx: SetContext, deps: VanguardPipeline):
		while (True):
			try:
				print("Welcome to VanguardTCGScrapper\n")
				print("What info do you need from the website?")

				for k,v in OPTIONS.items():
					print(f'{k}: {v}')

				user_input = convert_to_int((input("> ").strip().lower()))
				if (user_input not in OPTIONS):
					continue
				break
			except ValueError as e:
				print(f"Not valid input: {e}\n")
				continue

		answer = OPTIONS.get(user_input)
		set_ctx.category = answer

	@staticmethod
	def	select_subcategory(set_ctx: SetContext, deps: VanguardPipeline):
		options = CATEGORIES.get(set_ctx.category)
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
		set_ctx.subcategory = options[answer]

	@staticmethod
	def	make_query(set_ctx: SetContext, deps: VanguardPipeline):
		prefix = dispatcher(set_ctx)
		if (prefix is None):
			raise ValueError("No element selected in query dispatcher")
		param = {
			"action": "parse",
			"page": f"{prefix}",
			"format": "json"
		}
		set_ctx.query_page = prefix
		set_ctx.query_parameters = param

	@staticmethod
	def	parse_links(set_ctx: SetContext, deps: VanguardPipeline):
		links = deps.scrapper.obtain_links(set_ctx.response)
		deps.parser.clean_trash_from_set(set_ctx.query_page, links, 4)
		set_ctx.links = remove_from_list(links, [
			set_ctx.query_page,
			*DICT_S.get(set_ctx.category)
		])
		process_items(set_ctx.links, deps)
		if (set_ctx.category == "boosters"):
			sort_storage_list(["LB", "G"], deps)
		sort_storage_list(VALID_DATABASES, deps)

	@staticmethod
	async def	set_api_consult(set_ctx: SetContext, deps: VanguardPipeline):
		rules = construct_rules(
			set_ctx.query_parameters["page"].split()[4]
		)
		await smart_sleep()
		deps.classifier._define_rules(rules)
		param = set_ctx.query_parameters
		response = await deps.scrapper.api.get(
			param,
			HEADER
		)
		error = response.get("Error")
		if (error is not None):
			raise RuntimeError(f"Wiki API returned error: {response}")
		set_ctx.response = response

	@staticmethod
	def	__parser(set_ctx: SetContext, deps: VanguardPipeline):
		wikitex = deps.scrapper.obtain_wikitex(set_ctx.api_result)
		set_ctx.crude_cards = deps.parser.make_cardlist_from_str(wikitex)
		set_ctx.infobox = deps.parser.infobox(wikitex)
		all_links = deps.scrapper.obtain_links(set_ctx.links)
		deps.parser.clean_trash_from_set(set_ctx.query_parameters["page"], all_links, 4, reverse=True)
		set_ctx.links = deps.parser.sort_unique_url(
			set_ctx.crude_cards, all_links
		)

	@staticmethod
	async def	main_scrap_routine(set_ctx: SetContext, deps: VanguardPipeline):
		for block in VALID_DATABASES:
			database = getattr(deps.storage, block.lower())
			consult = deps.parser.make_consults(database, "consult")
			for set_number, tpl in consult.items():
				try:
					snapshot = deps.storage.link_storage.get_snapshot()
					if (check_data_base.set_exists(set_ctx, block, set_number)):
						print(
							f"Skiping existing set: "
							f"{block} {set_number + 1}"
						)
						continue
					set_ctx.tpl = tpl
					await deps.scrapper.api_calls(set_ctx)
					VanguardRoutine.__parser(set_ctx, deps)
					set_ctx.is_d = block in ["D", "DZ"]
					rows = deps.storage.prepare_metadata(set_ctx.crude_cards, set_ctx)
					columns = column_dispatcher(set_ctx)
					df = pd.DataFrame(rows, columns=columns)
					path = check_data_base.build_set_path(
						category=set_ctx.category,
						set_type=set_ctx.subcategory.strip().lower().split()[0],
						block=block,
						set_number=set_number + 1
					)
					path.parent.mkdir(
						parents=True,
						exist_ok=True
					)
					path = check_data_base.get_duplicate_path(path)
					df.to_parquet(path)
					print(df)
					if (set_ctx.is_deck == True):
						set_ctx.is_deck = False
				except (KeyError, ValueError, AttributeError, TypeError, IndexError) as e:
					print(f"Current set {tpl.get("titles")} gave the error: {e}")
					deps.storage.link_storage.rollback(snapshot)
					set_ctx.is_deck = False
					continue

	@staticmethod
	def	ask_user(set_ctx: SetContext, deps: StateMachine):
		while (True):
			print("Do you wish to continue with the web scrapping? [y]es, [n]o: ")
			answer = input(str("> ").strip().lower())
			if (answer not in ["y", "n"]):
				print("Invalid answer")
				continue
			if (answer == "y"):
				return (PipelineState.ENTRY_POINT)
			return (PipelineState.FINISH)
				