# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    scrap.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 20:09:12 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 20:09:12 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from pathlib						import Path

# Dependencies
import pandas 						as pd

# Library
from api_builder.api_request		import header
from api_builder.fsm.states			import State
from cards.fsm						import CardFSM
from utils.utils					import smart_sleep
from cards.states					import ParserState
from data.check_data_base			import build_set_path
from pipeline.builder				import VanguardPipeline

def	get_duplicate_path(path: Path) -> Path:
	if not path.exists():
		return path
	
	stem = path.stem
	suffix = path.suffix
	parent = path.parent
	i = 1
	while True:
		new_path = parent / f"{stem}_{i}{suffix}"
		if not new_path.exists():
			return new_path
		i += 1

def	define_param(tpl: dict):
	links = {
		"action": "parse",
		"page": tpl.get("titles"),
		"prop": "links",
		"format": "json"
	}
	return (links)

def	parser(card_fsm: CardFSM, pipeline: VanguardPipeline):
	wikitex = pipeline.scrapper.obtain_wikitex(card_fsm.fsm_context.data["api_result"])
	card_fsm.fsm_context.data["crude_cards"] = pipeline.scrapper.make_cardlist_from_str(wikitex)
	card_fsm.context.infobox = pipeline.parser.infobox(wikitex)
	all_links = pipeline.scrapper.obtain_links(card_fsm.fsm_context.data["link_result"])
	pipeline.parser.clean_trash_from_set(card_fsm.fsm_context.data["page"], all_links, 4, reverse=True)
	card_fsm.context.links = pipeline.parser.sort_unique_url(
		card_fsm.fsm_context.data["crude_cards"], all_links
	)

async def	make_api_calls(card_fsm: CardFSM, pipeline: VanguardPipeline):
	card_fsm.fsm_context.data["link_param"] = define_param(card_fsm.fsm_context.data["tpl"])
	await smart_sleep()
	card_fsm.fsm_context.data["api_result"] = await pipeline.scrapper.api.get(
		params=card_fsm.fsm_context.data["tpl"],
		headers=header
	)
	await smart_sleep()
	card_fsm.fsm_context.data["link_result"] = await pipeline.scrapper.api.get(
		params=card_fsm.fsm_context.data["link_param"],
		headers=header
	)

def	column_dispatcher(fsm: CardFSM):
	dispatcher = {
		"table": ["Code", "Name", "Grade",
				"Faction", "FactionType", "Type",
				"Rarity", "Release", "URL", "SET_ID"],
		"deck": ["Code", "Amount", "Name",
				"Grade", "Faction", "FactionType",
				"Type", "Release", "URL"]
	}
	return (dispatcher[fsm.fsm_context.data["columns"]])

async def	main_scrap_routine(card_fsm: CardFSM, pipeline: VanguardPipeline):
	for block in ["LB", "LL", "G", "V", "D", "DZ"]:
		consult = pipeline.parser.make_consults(getattr(pipeline.storage, block.lower()), "consult")
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
