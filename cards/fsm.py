# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    card_parser                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/12 17:52:03 by marvin            #+#    #+#              #
#    Updated: 2026/05/12 17:52:03 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.wikicode import Wikicode

# Library
from api_builder.fsm.constants	import NATIONS
from api_builder.fsm.fsm		import FSMContext
from cards.states				import ParserState
from cards						import cards_parser

class	ParserContext:
	def	__init__(self):
		self.reset()

	def	reset(self):
		self.link_key:		int = 0
		self.size:			int = 0
		self.prepare_data:	int = None
		self.infobox:		dict = None
		self.row:			list = None
		self.is_d:			bool = False
		self.is_deck:		bool = False
		self.obj:			object = None
		self.card:			list[str] = None
		self.rows:			list[object] = []
		self.links:			dict = None
		self.is_duplicated:	bool = None
		self.index:			int = 0

class	CardFSM:
	def	__init__(self, fsm_context: FSMContext):
		self.fsm_context =	fsm_context
		self.context =		ParserContext()
		self.state =		ParserState.START

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
				nations.append(i)
				continue
			card.append(i)
		self.context.card.insert(3, nations)
		return (card)
	
	def	__promo(self, data: list):
		pass

	def __decks(self, data: list):
		pass

	def __normalize_length(self):
		i = 0
		if (self.context.size == 8):
			self.state = ParserState.DUAL_CARD
			return
		while (self.context.size != 6):
			try:
				if (self.context.card[i] == '' or
						self.context.card[i] == "V" or
						self.context.card[i] == "D" or
						self.context.card[i] == "DZ"):
					self.context.card.pop(i)
					i = 0
					self.context.size = len(self.context.card)
				i += 1
				self.context.size = len(self.context.card)
			except (IndexError):
				break

	def	__dispatcher(self):
		self._dispatcher = {
			ParserState.DUAL_NATION: {
				"prepare": self.__dual_nations,
				"parse": cards_parser.parse_single_card,
				"cards": 1
			},
			ParserState.DUAL_CARD: {
				"prepare": self.__split_card,
				"parse": cards_parser.parse_dual_cards,
				"cards": 1
			},
			ParserState.SINGLE_CARD: {
				"prepare": None,
				"parse": cards_parser.parse_single_card,
				"cards": 1
			},
			ParserState.DECK: {
				"prepare": self.__decks,
				"parse": cards_parser.parse_deck,
				"cards": 0
			},
			ParserState.PROMO: {
				"prepare": self.__promo,
				"parse": cards_parser.parse_single_card,
				"cards": 1
			}
		}

	def	run(self, card: list[Wikicode]):
		self.__dispatcher()
		self.context.card = card
		self.context.size = len(self.context.card)
		self.__normalize_length()
		nations = sum(
			1 for nation in self.context.card
			if (str(nation) in NATIONS)
		)

		if (self.state == ParserState.DUAL_CARD):
			return
		if (nations >= 2):
			self.state = ParserState.DUAL_NATION
		elif (self.fsm_context.main_category == "decks"):
			self.state = ParserState.DECK
		else:
			self.state = ParserState.SINGLE_CARD
		
		handler = self._dispatcher[self.state]
		data = self.context.card
		if (handler["prepare"]):
			data = handler["prepare"](data)
		self.context.row = handler["parse"](data)
		self.context.prepare_data = handler["cards"]
