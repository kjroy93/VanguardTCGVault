# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    classifier.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/04 10:15:14 by marvin            #+#    #+#              #
#    Updated: 2026/05/04 10:15:14 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from pipeline.builder	import VanguardPipeline

def	process_items(data: list, pipeline: VanguardPipeline):
	for i in data:
		key = pipeline.classifier.classify(i)
		pipeline.storage._add_item(key, i)

def	sort_storage_list(attributes: list[str], pipeline: VanguardPipeline):
	for atrribute in attributes:
		lst = getattr(pipeline.storage, atrribute.lower(), [])
		if (not lst):
			continue
		lst.sort(key=pipeline.classifier.obtain_set_number)
