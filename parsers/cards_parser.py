# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards_parser.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 16:52:57 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/18 00:40:31 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from dataclasses				import dataclass
from typing						import Callable, Union, Literal

# Library
from utils						import utils
from utils.constants			import NATIONS
from cards.fsm					import CardContext
from parsers.types				import MetadataType, CardType

@dataclass
class	CardsParser:
	@staticmethod
	def	raw_table_data_prepare(template: list,
	                              control: Literal["card", "deck"]
								  = "card") -> list:
		data = []
		columns = [0, 1, 2, 3, 4, 5]
		for i in columns:
			if (i == 2):
				information = utils.convert_to_int(template[i])
			if (control == "deck" and i == 5):
				information = utils.convert_to_int(template[i])
			else:
				if (isinstance(template[i], list)):
					continue
				information = utils.convert_to_str(template[i])
			data.append(information)
		return (data)

	@staticmethod
	def	parse_dual_cards(cards: list[list[str | int]]):
		l = []
		for card in cards:
			parsed_row = CardsParser.raw_table_data_prepare(card)
			l.append(parsed_row)
		return (l)

	@staticmethod
	def	parse_card(card_ctx: CardContext, control: str):
		if (card_ctx.name == "CardListV"):
			card = []
			
			for i, template in enumerate(card_ctx.card):
				if (i != 2):
					card.append(template)
			parsed_row = CardsParser.raw_table_data_prepare(card)	
			return (parsed_row)
		
		if (control != "deck"):
			parsed_row = CardsParser.raw_table_data_prepare(card_ctx)
		else:
			parsed_row = CardsParser.raw_table_data_prepare(card_ctx, "deck")
		return (parsed_row)

	@staticmethod
	def validate_row_length(card_ctx: CardContext):
		if (card_ctx.size != 6 or card_ctx.size != 8):
			raise ValueError(
				f"Amount of data invalid in card {card_ctx.card}: {card_ctx.row!r}"
			)

	def	__split_card(self, card_ctx: CardContext):
		if (len(card_ctx.size) != 8):
			raise ValueError(f"Expected 8 parameters: {card_ctx.card!r}")

		code, name_a, grade_a, name_b, grade_b, faction, card_type, rarity = card_ctx.card
		return [
			[code, name_a, grade_a, faction, card_type, rarity],
			[code, name_b, grade_b, faction, card_type, rarity],
		]

	def	__dual_nations(self, card_ctx: CardContext):
		nations = []
		card = []
		for i in card_ctx.card:
			if (str(i) in NATIONS):
				nation = str(i)
				nations.append(nation)
				continue
			card.append(i)
		card.insert(3, nations)
		card_ctx.card = card
	
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
				"parse": CardsParser.parse_card,
				"cards": MetadataType.SINGLE
			},
			CardType.PROMO: {
				"prepare": self.__promo,
				"parse": CardsParser.parse_card,
				"cards": MetadataType.SINGLE
			},
			CardType.DUAL_NATION: {
				"prepare": self.__dual_nations,
				"parse": CardsParser.parse_card,
				"cards": MetadataType.SINGLE
			},
			CardType.DUAL_CARD: {
				"prepare": self.__split_card,
				"parse": CardsParser.parse_dual_cards,
				"cards": MetadataType.DUAL
			},
			CardType.DECK: {
				"prepare": self.__decks,
				"parse": CardsParser.parse_card,
				"cards": MetadataType.DECK
			}
		}
		return (dispatcher[card_type])

	def	get_handler(self, card_type: CardType):
		return (self._dispatcher(card_type))