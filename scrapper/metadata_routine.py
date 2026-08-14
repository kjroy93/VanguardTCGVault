# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    metadata_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:02:26 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 21:22:30 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from enum					import Enum, auto

# Library
from utils.constants		import NATIONS
from cards.fsm				import CardContext
from parsers.cards_parser	import CardType, CardsParser

class	MetadataType(Enum):
	DECK	= auto()
	SINGLE	= auto()
	DUAL	= auto()

class	MetadataRoutine:
	def	__init__(self, parser: CardsParser):
		self.parser = parser

	def __classify(self, ctx: CardContext) -> CardType:
		if (len(ctx.card)) == 8:
			return (CardType.DUAL_CARD)

		nations = sum(
			1
			for value in ctx.card
			if str(value) in NATIONS
		)

		if (nations >= 2):
			return (CardType.DUAL_NATION)

		if (ctx.is_deck):
			return (CardType.DECK)

		return (CardType.SINGLE_CARD)

	def	run(self, ctx: CardContext):
		card = ctx.card
		card_type = self.__classify(ctx)
		handler = self.parser.get_handler(card_type)
		data = card

		if (handler["prepare"] is not None):
			data = handler["prepare"](data)

		ctx.row = handler["parse"](data)
		ctx.prepare_data = handler["cards"]

		if (card_type != CardType.DUAL_CARD):
			ctx.size = len(ctx.row)
			self.parser.normalize_length(ctx)
		self.parser.normalize_length(ctx)

		return (ctx.row)
