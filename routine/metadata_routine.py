# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    metadata_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:02:26 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/15 18:13:45 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from utils.constants		import NATIONS
from parsers.types			import CardType
from routine.fsm			import SetContext
from cards.fsm				import CardContext
from parsers.cards_parser	import CardsParser

class	MetadataRoutine:
	def	__init__(self, parser: CardsParser):
		self.parser = parser

	def __classify(self, card_ctx: CardContext, set_ctx: SetContext) -> CardType:
		if (len(card_ctx.card)) == 8:
			return (CardType.DUAL_CARD)

		nations = sum(
			1
			for value in card_ctx.card
			if str(value) in NATIONS
		)

		if (nations >= 2):
			return (CardType.DUAL_NATION)

		if (set_ctx.is_deck):
			return (CardType.DECK)

		return (CardType.SINGLE_CARD)

	def	run(self, card_ctx: CardContext, set_ctx: SetContext):
		card = card_ctx.card
		card_type = self.__classify(card_ctx, set_ctx)
		handler = self.parser.get_handler(card_type)
		data = card

		if (handler["prepare"] is not None):
			data = handler["prepare"](data)

		card_ctx.row = handler["parse"](data)
		card_ctx.prepare_data = handler["cards"]

		if (card_type != CardType.DUAL_CARD):
			card_ctx.size = len(card_ctx.row)
			self.parser.normalize_length(card_ctx)
		self.parser.normalize_length(card_ctx)

		return (card_ctx.row)
