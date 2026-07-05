# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_classifier.py                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:22:01 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:22:01 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import re

class	VanguardClassifier:
	def _define_rules(self, rules):
		self._rules = rules

	def	obtain_set_number(self, play_set: str):
		number = ""
		for i in play_set:
			if (i.isdigit()):
				number += i
			elif (number):
				break
		if (number == ""):
			return (-1)
		return (int(number))

	def	classify(self, name: str) -> str:
		num = self.obtain_set_number(name)
		if (num in (16, 17) and "Booster" in name):
			return ("LL")
		for pattern, key in self._rules:
			if (re.match(pattern, name)):
				return (key)
		return ("LB")
