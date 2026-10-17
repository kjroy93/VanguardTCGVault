# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    metadata_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:02:26 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/17 22:40:32 by kjroydev         ###   ########.fr        #
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
		nations = sum(
			1
			for param in card_ctx.card
			if str(param.value).strip() in NATIONS
		)
		
		if (card_ctx.size == 8 and nations != 2):
			return (CardType.DUAL_CARD)

		if (card_ctx.size == 8 and nations == 2):
			return (CardType.DUAL_NATION)

		if ("Deck" in set_ctx.tpl.get("titles")):
			set_ctx.is_deck = True

		if (set_ctx.is_deck):
			return (CardType.DECK)

		return (CardType.SINGLE_CARD)

	def	run(self, card_ctx: CardContext, set_ctx: SetContext):
		card_type = self.__classify(card_ctx, set_ctx)
		handler = self.parser.get_handler(card_type)
		data = card_ctx.card

		if (handler["prepare"] is not None):
			data = handler["prepare"](data)

		card_ctx.row = handler["parse"](data)
		card_ctx.prepare_data = handler["cards"]
		self.parser.validate_row_length(card_ctx.row)

		return (card_ctx.row)
