# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 16:07:31 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 16:07:31 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import time

# Dependencies
import pandas as pd

# Library
from utils.utils import remove_from_list
from parsers.rules import construct_rules
from pipeline.builder import VanguardPipeline
from data.vanguard_data import VanguardStorage
from parsers.vanguard_parser import VanguardParser
from api_builder.api_request import header, first_param
from classifier.vanguard_classifier import VanguardClassifier
from classifier.classifier import process_items, sort_storage_list
from api_builder.vanguard_api_build import MediaWikiAPI, VanguardScrapper

# Url Parser
rules = construct_rules("Booster")
web = MediaWikiAPI()
pipeline = VanguardPipeline(
	VanguardScrapper(web),
	VanguardParser(),
	VanguardClassifier(rules),
	VanguardStorage()
)

def	request_to_api():
	pass
api_answer = pipeline.scrapper.api.get(params=first_param, headers=header)
crude_data = pipeline.scrapper.obtain_links(api_answer)
crude_consults = pipeline.parser.separate_urls(crude_data)
crude_consults = remove_from_list(crude_consults, [
	"Lyrical Monasterio", "The Mask Collection"
])
consults = pipeline.parser.make_consults("get", crude_consults)
crude_data = remove_from_list(crude_data, [
	"G Booster Set 8: Collezione del Combattente Vol.1",
	"G Booster Set 9: Collezione del Combattente Vol.2",
	"Thailand Booster Set 1: The Mask Collection",
	"G Booster Set 7: Giudizio delle Lame Splendenti",
	"G Booster Set 1: Trascendenza Interdimensionale"
])
process_items(crude_data, pipeline.classifier, pipeline.storage)
sort_storage_list(["LB", "G"], pipeline.classifier, pipeline.storage)
time.sleep(2)
dz_consults = pipeline.parser.make_consults("consult", pipeline.storage.dz)
api_answer = pipeline.scrapper.api.get(params=dz_consults[0], headers=header)
wikitex = pipeline.scrapper.obtain_wikitex(api_answer)
data = pipeline.scrapper.make_cardlist_from_str(wikitex=wikitex)
infobox = pipeline.parser.infobox(wikitex)
rows = pipeline.storage.prepare_data(data, 6, is_d=True, infobox=infobox)
df = pd.DataFrame(rows, columns=[
	"CardNo", "Name", "Grade", "Faction",
	"FactionType", "Type", "Rarity", "Release"
])
