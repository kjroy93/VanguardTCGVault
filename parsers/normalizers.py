# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    normalizers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:18:17 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:18:17 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.nodes import Template

# Library
from fsm.menus import NATIONS

def	convert_to_str(element: Template):
	return (str(element.value).strip())

def	convert_to_int(element: str):
	if (element.isdigit()):
		return (int(element))
	raise ValueError

def	split_cards(data: list):
	card_a = []
	card_b = []
	i = 5
	if (len(data) > 6):
		card_a = data[0:3]
		card_b = data[3:]
	while (len(card_b) < 6):
		card_b.insert(0, card_a[0])
	while (len(card_a) < 6):
		card_a.insert(3, card_b[i])
		i -= 1
	return ([card_a, card_b])

def	dual_nations(data: list):
	nations = []
	card = []
	for i in data:
		if (str(i) in NATIONS):
			nations.append(i)
			continue
		card.append(i)
	card.insert(3, nations)
	return (card)

def normalize_length(data: list, size: int):
	i = 0
	lenght = len(data)
	if (lenght > size):
		result = split_cards(data)
		return (result)
	while (lenght != size):
		try:
			if (data[i] == '' or
	   				data[i] == "V" or
					data[i] == "D" or
					data[i] == "DZ"):
				data.pop(i)
				i += 1
			i += 1
			lenght = len(data)
		except IndexError:
			break
	return (data)

def	raw_table_data_prepare(template: list):
	data = []
	for i in template:
		raw_value = convert_to_str(i)
		try:
			value = convert_to_int(raw_value)
		except ValueError:
			value = raw_value
		if (value != None):
			data.append(value)
	return (data)
