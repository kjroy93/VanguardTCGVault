# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards_parser.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 16:52:57 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/17 22:52:47 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from dataclasses				import dataclass
from typing						import Callable, Union

# Library
from utils						import utils
from utils.constants			import NATIONS
from cards.fsm					import CardContext
from parsers.types				import MetadataType, CardType

@dataclass
class	CardsParser:
	@staticmethod
	def	raw_table_data_prepare(template: list) -> list:
		data = []
		columns = [0, 1, 2, 3, 4, 5]
		for i in columns:
			if (i == 2):
				information = utils.convert_to_int(template[i])
			else:
				information = utils.convert_to_str(template[i])
			data.append(information)
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
	def	parse_deck(card: list[str | int]):
		parsed_row = CardsParser.raw_table_data_prepare(card)
		return (parsed_row)

	@staticmethod
	def validate_row_length(card_ctx: CardContext):
		if (card_ctx.size != 6 or card_ctx.size != 8):
			raise ValueError(
				f"Amount of data invalid in card {card_ctx.card}: {card_ctx.row!r}"
			)

	def	__split_card(self, data: list):
		if (len(data) != 8):
			raise ValueError(f"Expected 8 parameters: {data!r}")

		code, name_a, grade_a, name_b, grade_b, faction, card_type, rarity = data
		return [
			[code, name_a, grade_a, faction, card_type, rarity],
			[code, name_b, grade_b, faction, card_type, rarity],
		]

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
		result = sum(
			1 for nation in NATIONS
			if nation in data
		)
		if (result > 1):
			card = self.__dual_nations(data)
			return (card)
		card = data
		return (card)

	def	_dispatcher(self, card_type: CardType) -> dict[str, Union[Callable | int]]:
		dispatcher = {
			CardType.SINGLE_CARD: {
				"prepare": None,
				"parse": CardsParser.parse_single_card,
				"cards": MetadataType.SINGLE
			},
			CardType.PROMO: {
				"prepare": self.__promo,
				"parse": CardsParser.parse_single_card,
				"cards": MetadataType.SINGLE
			},
			CardType.DUAL_NATION: {
				"prepare": self.__dual_nations,
				"parse": CardsParser.parse_single_card,
				"cards": MetadataType.SINGLE
			},
			CardType.DUAL_CARD: {
				"prepare": self.__split_card,
				"parse": CardsParser.parse_dual_cards,
				"cards": MetadataType.DUAL
			},
			CardType.DECK: {
				"prepare": self.__decks,
				"parse": CardsParser.parse_deck,
				"cards": MetadataType.DECK
			}
		}
		return (dispatcher[card_type])

	def	get_handler(self, card_type: CardType):
		return (self._dispatcher(card_type))