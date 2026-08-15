# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vanguard_classifier.py                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:22:01 by marvin            #+#    #+#              #
#    Updated: 2026/08/15 19:23:40 by kjroydev         ###   ########.fr        #
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
		if (
			name.startswith("Booster Set")
			and self.obtain_set_number(name) in (16, 17)
		):
			return ("LL")
		for pattern, key in self._rules:
			if (re.match(pattern, name)):
				return (key)
		return ("LB")
