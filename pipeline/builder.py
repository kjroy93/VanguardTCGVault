# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    builder.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/04 16:19:46 by marvin            #+#    #+#              #
#    Updated: 2026/08/13 16:24:55 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from parsers.vanguard_parser		import VanguardParser
from data.vanguard_data				import VanguardStorage
from wiki_api.vanguard_api			import VanguardScrapper
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
