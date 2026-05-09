# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    parse.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 13:28:03 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 13:28:03 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from fsm.states						import State
from fsm.fsm						import FSMContext
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from api_builder.vanguard_api_build	import VanguardScrapper
from utils.utils					import remove_from_list
from classifier.vanguard_classifier import VanguardClassifier
from classifier.classifier 			import process_items, sort_storage_list

dict_s = {
	"boosters": [
		"List",
		"Unique",
		"G Booster Set 14: Divine Dragon Apocrypha",
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

def	parse_links(fsm: FSMContext,
				parser: VanguardParser,
				storage: VanguardStorage,
				scrapper: VanguardScrapper,
				classifier: VanguardClassifier):
	links = scrapper.obtain_links(fsm.data["response"])
	parser.clean_trash_from_set(fsm.data["page"], links, 4)
	parsed_links = remove_from_list(links, [
		fsm.data["page"],
		*dict_s.get(fsm.main_category)
	])
	process_items(parsed_links, classifier, storage)
	if (fsm.answer == "boosters"):
		sort_storage_list(["LB", "G"], classifier,storage)
	sort_storage_list([], classifier,storage)
	fsm.data["parsed_links"] = parsed_links
	fsm.current_state = State.END
	return (fsm.current_state)
