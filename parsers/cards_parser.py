# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards_parser.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 16:52:57 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/18 02:33:28 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from dataclasses					import dataclass
from typing							import Callable, Union, Literal

# Dependencies
from mwparserfromhell.nodes.extras	import Parameter

# Library
from utils							import utils
from utils.constants				import NATIONS
from cards.fsm						import CardContext
from parsers.types					import MetadataType, CardType

@dataclass
class	CardsParser:
	@staticmethod
	def	raw_table_data_prepare(template: list[Parameter],
								control: Literal["card", "deck"]
								= "card") -> list:
		data = []
		for i, param in enumerate(template):
			if (isinstance(param, list)):
				data.append(param)
				continue

			value = str(
				param.value if hasattr(param, "value") else param
			).strip()

			if (value == ""):
				data.append(None)
				continue
			if (i == 2 or (control == "deck" and i == 5)):
				information = utils.convert_to_int(value)
			else:
				information = value
			data.append(information)
		return (data)

	@staticmethod
	def	__split_card(card_ctx: CardContext):
		if (card_ctx.size != 8):
			raise ValueError(f"Expected 8 parameters: {card_ctx.card!r}")

		code, name_a, grade_a, name_b, grade_b, faction, card_type, rarity = card_ctx.card
		return [
			[code, name_a, grade_a, faction, card_type, rarity],
			[code, name_b, grade_b, faction, card_type, rarity],
		]

	@staticmethod
	def	parse_dual_cards(card_ctx: CardContext):
		l = []
		cards = CardsParser.__split_card(card_ctx)
		for card in cards:
			parsed_row = CardsParser.raw_table_data_prepare(card)
			l.append(parsed_row)
		return (l)

	@staticmethod
	def	parse_card(card_ctx: CardContext, control: Literal["deck", "card"] = "card"):
		if (card_ctx.name == "CardListV"):
			card = []
			
			for i, template in enumerate(card_ctx.card):
				if (i != 2):
					card.append(template)
			parsed_row = CardsParser.raw_table_data_prepare(card)	
			return (parsed_row)
		
		if (control != "deck"):
			parsed_row = CardsParser.raw_table_data_prepare(card_ctx.card)
		else:
			parsed_row = CardsParser.raw_table_data_prepare(card_ctx.card, "deck")
		return (parsed_row)

	@staticmethod
	def validate_row_length(row: list):
		if (isinstance(row[0], list)):
			for r in row:
				if (len(r) != 6):
					raise ValueError(f"Expected 6 fields: {row!r}")
			return (None)
		if (len(row) != 6):
			raise ValueError(f"Expected 6 fields: {row!r}")

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

	def __decks(self, card_ctx: CardContext):
		result = sum(
			1 for nation in NATIONS
			if nation in card_ctx.card
		)
		if (result > 1):
			self.__dual_nations(card_ctx.card)

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
				"prepare": None,
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