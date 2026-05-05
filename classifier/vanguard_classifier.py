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
	def	__init__(self):
		self._rules = [
			(r"^DZ", "DZ"),
			(r"^D", "D"),
			(r"^G", "G"),
			(r"^V", "V"),
			(r"^Booster", "LB")
		]

	def	obtain_set_number(self, play_set: str):
		number = ""
		for i in play_set:
			if (i.isdigit()):
				number += i
			elif (number):
				break
		return (int(number))

	def	classify(self, name: str) -> str:
		num = self.obtain_set_number(name)
		if (num in (16, 17) and "Booster" in name):
			return ("LL")
		for pattern, key in self._rules:
			if (re.match(pattern, name)):
				return (key)
		return ("LB")
