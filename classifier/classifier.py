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

from data.vanguard_data import VanguardStorage
from classifier.vanguard_classifier import VanguardClassifier

def	process_items(data: list, classifier: VanguardClassifier, storage: VanguardStorage):
	for i in data:
		key = classifier.classify(i)
		storage._add_item(key, i)

def	sort_storage_list(attributes: list[str],
					classifier: VanguardClassifier,
					storage: VanguardStorage):
	for atrribute in attributes:
		lst = getattr(storage, atrribute.lower())
		lst.sort(key=classifier.obtain_set_number)
