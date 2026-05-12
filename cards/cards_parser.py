# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards_parser.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/12 18:12:51 by marvin            #+#    #+#              #
#    Updated: 2026/05/12 18:12:51 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from utils import utils

def	raw_table_data_prepare(template: list) -> list:
	data = []
	for i in template:
		raw_value = utils.convert_to_str(i)
		try:
			value = utils.convert_to_int(raw_value)
		except (ValueError):
			value = raw_value
		if (value != None):
			data.append(value)
	return (data)

def	parse_single_card(card: list[str | int]):
	parsed_row = raw_table_data_prepare(card)
	return (parsed_row)

def	parse_dual_cards(cards: list[list[str | int]]):
	parsed_row = []
	for card in cards:
		parsed_row = raw_table_data_prepare(card)
		parsed_row.append(card)
	return (parsed_row)

def	parse_deck():
	pass