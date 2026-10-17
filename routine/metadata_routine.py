# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    metadata_routine.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:02:26 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/18 01:04:20 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from parsers.types			import CardType
from routine.fsm			import SetContext
from cards.fsm				import CardContext
from parsers.cards_parser	import CardsParser

class	MetadataRoutine:
	def	__init__(self, parser: CardsParser):
		self.parser = parser

	def __classify(self, card_ctx: CardContext, set_ctx: SetContext) -> CardType:
		template_types = {
			"CardList": CardType.SINGLE_CARD,
			"CardListV": CardType.SINGLE_CARD,
			"CardList2": CardType.DUAL_CARD,
			"CardList2N": CardType.DUAL_NATION,
			"Deck": CardType.DECK
		}
		
		if ("Deck" in set_ctx.tpl.get("titles")):
			set_ctx.is_deck = True
			card_type = template_types.get("Deck")
			return (card_type)

		card_type = template_types.get(card_ctx.name)

		if (card_type is None):
			raise ValueError(
				f"Unknown card template: "
				+ f"{card_ctx.name}"
				+ f"{set_ctx.tpl.get("titles")}"
			)

		return (card_type)

	def	run(self, card_ctx: CardContext, set_ctx: SetContext):
		card_type = self.__classify(card_ctx, set_ctx)
		handler = self.parser.get_handler(card_type)

		if (handler["prepare"] is not None):
			handler["prepare"](card_ctx)

		card_ctx.row = handler["parse"](card_ctx)
		card_ctx.prepare_data = handler["cards"]
		self.parser.validate_row_length(card_ctx.row)

		return (card_ctx.row)
