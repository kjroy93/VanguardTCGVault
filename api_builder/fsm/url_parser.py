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
from api_builder.fsm.states			import State
from api_builder.fsm.fsm			import FSMContext
from pipeline.builder				import VanguardPipeline
from utils.utils					import remove_from_list
from classifier.classifier 			import process_items, sort_storage_list

dict_s = {
	"boosters": [
		"List",
		"Unique",
		"G Booster Set 5: Ombre Assassine",
		"G Booster Set 6: Tempesta di Fiori",
		"G Booster Set 4: La Debolezza è un Peccato",
		"Thailand Booster Set 1: The Mask Collection",
		"G Booster Set 1: Trascendenza Interdimensionale",
		"G Booster Set 7: Giudizio delle Lame Splendenti",
		"G Booster Set 8: Collezione del Combattente Vol.1",
		"G Booster Set 9: Collezione del Combattente Vol.2",
		"G Booster Set 3: Potere Supremo del Drago Stellare",
		"G Booster Set 2: Assalto Fulmineo delle Fiamme Roventi",
	],
	"specials": [
		"List",
		"Thailand"
	],
	"decks": [
		"List",
		"Thailand"
	]
}

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

def	parse_links(fsm: FSMContext, pipeline: VanguardPipeline):
	links = pipeline.scrapper.obtain_links(fsm.data["response"])
	pipeline.parser.clean_trash_from_set(fsm.data["page"], links, 4)
	parsed_links = remove_from_list(links, [
		fsm.data["page"],
		*dict_s.get(fsm.main_category)
	])
	process_items(parsed_links, pipeline)
	if (fsm.answer == "boosters"):
		sort_storage_list(["LB", "G"], pipeline)
	sort_storage_list([], pipeline)
	fsm.current_state = State.SCRAP
	return (fsm.current_state)
