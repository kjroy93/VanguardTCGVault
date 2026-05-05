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
import mwparserfromhell
from mwparserfromhell.nodes	import Template

# Library
from utils.utils import remove_from_list
from cards.classes import ScrapCard
from pipeline.builder import VanguardPipeline
from data.vanguard_data import VanguardStorage
from classifier.classifier import process_items, sort_storage_list
from parsers.vanguard_parser import VanguardParser
from api_builder.vanguard_api_build import MediaWikiAPI, VanguardScrapper
from classifier.vanguard_classifier import VanguardClassifier

# Definition
JSONType = dict[str]
header = {
	"User-Agent": "VanguardScrapper/1.0 (Python; contact: kmarrero1993@gmail.com)"
}
first_param = {
	"action": "parse",
	"page": "List of Cardfight!! Vanguard Booster Sets",
	"format": "json"
}
