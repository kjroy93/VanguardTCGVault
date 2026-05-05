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

class	VanguardPipeline:
	def	__init__(self, scrapper, parser, classifier, storage):
		self.scrapper =	scrapper
		self.parser = parser
		self.classifier = classifier
		self.storage = storage
