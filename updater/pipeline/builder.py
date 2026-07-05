# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    pipeline.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/04 16:19:46 by marvin            #+#    #+#              #
#    Updated: 2026/05/04 16:19:46 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from api_builder.vanguard_api_build	import VanguardScrapper
from classifier.vanguard_classifier	import VanguardClassifier

class	VanguardPipeline:
	def	__init__(self,
			  parser: VanguardParser,
			  storage: VanguardStorage,
			  scrapper: VanguardScrapper,
			  classifier: VanguardClassifier):
		self.parser = parser
		self.storage = storage
		self.scrapper =	scrapper
		self.classifier = classifier
