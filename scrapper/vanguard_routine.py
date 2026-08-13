# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/13 16:07:45 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/13 20:06:49 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
import pandas						as pd

# Library
from wiki_api.vanguard_api			import header
from pipeline.builder				import VanguardPipeline
from utils.constants				import DICT_S, CATEGORIES
from scrapper.fsm					import ParseContext as Context
from classifier.classifier			import process_items, sort_storage_list
from data.check_data_base			import build_set_path, get_duplicate_path
from utils.utils					import remove_from_list, smart_sleep, construct_rules, dispatcher

def	column_dispatcher(ctx: Context):
	dispatcher = {
		"table": ["Code", "Name", "Grade",
				"Faction", "FactionType", "Type",
				"Rarity", "Release", "URL", "SET_ID"],
		"deck": ["Code", "Amount", "Name",
				"Grade", "Faction", "FactionType",
				"Type", "Release", "URL"]
	}
	return (dispatcher[ctx.data["columns"]])

class	VanguardRoutine:
	@staticmethod
	def	select_category(ctx: Context, deps: VanguardPipeline):
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

		for k,v in options.items():
			print(f'{k}: {v}')
		
		while (True):
			user_input = int(input("> ").strip().lower())
			if (user_input not in options):
				continue
			break
		
		answer = options.get(user_input)
		ctx.category = answer
		ctx.column = dispatcher[answer]

	@staticmethod
	def	select_subcategory(ctx: Context, deps: VanguardPipeline):
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

	@staticmethod
	def	make_query(ctx: Context, deps: VanguardPipeline):
		prefix = dispatcher(ctx)
		if (prefix is None):
			raise ValueError("No element selected in query dispatcher")
		param = {
			"action": "parse",
			"page": f"{prefix}",
			"format": "json"
		}
		ctx.query_page = prefix
		ctx.query_parameters = param

	@staticmethod
	def	parse_links(ctx: Context, deps: VanguardPipeline):
		links = deps.scrapper.obtain_links(ctx.response)
		deps.parser.clean_trash_from_set(ctx.query_page, links, 4)
		parsed_links = remove_from_list(links, [
			ctx.response,
			*DICT_S.get(ctx.response)
		])
		process_items(parsed_links, deps)
		if (ctx.category == "boosters"):
			sort_storage_list(["LB", "G"], deps)
		sort_storage_list(["LB", "LL", "G", "V", "D", "DZ"], deps)

	@staticmethod
	async def	set_api_consult(ctx: Context, deps: VanguardPipeline):
		rules = construct_rules(
			ctx.query_parameters["page"].split()[4]
		)
		await smart_sleep()
		deps.classifier._define_rules(rules)
		param = ctx.query_parameters
		response = await deps.scrapper.api.get(
			param,
			header
		)
		error = response.get("Error")
		if (error is not None):
			raise RuntimeError(f"Wiki API returned error: {response}")
		ctx.response = response

	def	parser(self, ctx: Context, deps: VanguardPipeline):
		wikitex = deps.scrapper.obtain_wikitex(ctx.data["api_result"])
		ctx.data["crude_cards"] = deps.parser.make_cardlist_from_str(wikitex)
		ctx.infobox = deps.parser.infobox(wikitex)
		all_links = deps.scrapper.obtain_links(ctx.data["link_result"])
		deps.parser.clean_trash_from_set(ctx.data["page"], all_links, 4, reverse=True)
		ctx.crude_cards = deps.parser.sort_unique_url(
			ctx.data, all_links
		)

	async def	main_scrap_routine(self, ctx: Context, deps: VanguardPipeline):
		for block in ["LB", "LL", "G", "V", "D", "DZ"]:
			consult = deps.parser.make_consults(getattr(deps.storage, block.lower()), "consult")
			for tpl in consult.values():
				ctx.tpl = tpl
				await deps.scrapper.api_calls(ctx.tpl)
				self.parser(ctx, deps)
				if (block in ["D", "DZ"]):
					ctx.is_d = True
				try:
					rows = deps.storage.prepare_metadata(ctx.crude_cards, ctx)
				except (KeyError, ValueError, AttributeError) as e:
					return (e)
				columns = column_dispatcher(ctx)
				df = pd.DataFrame(rows, columns=columns)
				set_number = deps.classifier.obtain_set_number(
					ctx.crude_cards[0]
				)
				path = build_set_path(
					category=ctx.category,
					set_type=ctx.subcategory.strip().lower().split()[0],
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
