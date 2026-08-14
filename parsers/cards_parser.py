# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards_parser.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 16:52:57 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 19:26:28 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing				import Callable, Union
from dataclasses		import dataclass
from enum				import Enum, auto

# Library
from utils				import utils
from utils.constants	import NATIONS
from scrapper.fsm		import PipelineContext as Context

class	CardType(Enum):
	SINGLE_CARD	= auto()
	DUAL_CARD	= auto()
	DUAL_NATION	= auto()
	PROMO		= auto()
	DECK		= auto()

@dataclass
class	CardsParser:
	@staticmethod
	def	raw_table_data_prepare(template: list) -> list:
		data = []
		for i in template:
			try:
				raw_value = utils.convert_to_str(i)
			except (AttributeError):
				value = i
				data.append(value)
				continue
			try:
				value = utils.convert_to_int(raw_value)
			except (ValueError):
				value = raw_value
			if (value != None):
				data.append(value)
		return (data)

	@staticmethod
	def	parse_single_card(card: list[str | int]):
		parsed_row = CardsParser.raw_table_data_prepare(card)
		return (parsed_row)

	@staticmethod
	def	parse_dual_cards(cards: list[list[str | int]]):
		l = []
		for card in cards:
			parsed_row = CardsParser.raw_table_data_prepare(card)
			l.append(parsed_row)
		return (l)

	@staticmethod
	def	parse_deck():
		pass

	@staticmethod
	def normalize_length(ctx: Context):
		if (ctx.size < 6):
			ctx.row.insert(len(ctx.row), '')
		i = 0
		while (ctx.size != 6):
			try:
				if (ctx.row[i] == '' or
						ctx.row[i] == "V" or
						ctx.row[i] == "D" or
						ctx.row[i] == "DZ"):
					ctx.row.pop(i)
					i = 0
					ctx.size = len(ctx.row)
					continue
				i += 1
				ctx.size = len(ctx.row)
			except (IndexError):
				break

	def	__split_card(self, data: list):
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

	def	__dual_nations(self, data: list):
		nations = []
		card = []
		for i in data:
			if (str(i) in NATIONS):
				nation = str(i)
				nations.append(nation)
				continue
			card.append(i)
		card.insert(3, nations)
		return (card)
	
	def	__promo(self, data: list):
		pass

	def __decks(self, data: list):
		pass

	def	_dispatcher(self, card_type: CardType) -> dict[str, Union[Callable | int]]:
		dispatcher = {
			CardType.SINGLE_CARD: {
				"prepare": None,
				"parse": CardsParser.parse_single_card,
				"cards": 1
			},
			CardType.PROMO: {
				"prepare": self.__promo,
				"parse": CardsParser.parse_single_card,
				"cards": 1
			},
			CardType.DUAL_NATION: {
				"prepare": self.__dual_nations,
				"parse": CardsParser.parse_single_card,
				"cards": 1
			},
			CardType.DUAL_CARD: {
				"prepare": self.__split_card,
				"parse": CardsParser.parse_dual_cards,
				"cards": 2
			},
			CardType.DECK: {
				"prepare": self.__decks,
				"parse": CardsParser.parse_deck,
				"cards": 0
			}
		}
		return (dispatcher(card_type))