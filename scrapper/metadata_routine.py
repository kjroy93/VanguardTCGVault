# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    metadata_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:02:26 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 19:31:57 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from utils.constants		import NATIONS
from parsers.cards_parser	import CardType, CardsParser
from scrapper.fsm			import PipelineContext as Context

class	MetadataRoutine:
	def	__init__(self, parser: CardsParser):
		self.parser = parser

	def __classify(self, ctx: Context) -> CardType:
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

	def	run(self, ctx: Context):
		card = ctx.card
		card_type = self.__classify(ctx)
		handler = self.parser._dispatcher(card_type)
		data = card

		if (handler["prepare"] is not None):
			data = handler["prepare"](data)

		ctx.row = handler["parse"](data)
		ctx.prepare_data = handler["cards"]

		if (card_type != CardType.DUAL_CARD):
			ctx.size = len(ctx.row)
		self.parser.normalize_length(ctx)

		return (ctx.row)
