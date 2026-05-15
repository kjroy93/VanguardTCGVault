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
from mwparserfromhell.wikicode	import Wikicode

# Library
from api_builder.fsm.constants	import NATIONS
from api_builder.fsm.fsm		import FSMContext
from cards.states				import ParserState
from cards						import cards_parser

class ParserContext:
	"""
	Shared context used between the parser and the FSM.

	Attributes:
		size (int):
			Amount of processed elements.

		prepare_data (int):
			Defines the data preparation mode.

		infobox (dict):
			Information extracted from the wiki infobox.

		row (list):
			Temporary row currently being processed.

		is_d (bool):
			Indicates whether the entry belongs to D format.

		is_deck (bool):
			Indicates whether the parser is processing decks.

		obj (object):
			Output model used to build parsed data.

		card (list[str]):
			Temporary card-related information.

		rows (list[object]):
			Accumulated list of constructed models.

		links (dict):
			Mapping between names and URLs.

		is_duplicated (bool):
			Indicates whether the current entry already exists.

		index (int):
			Internal incremental index.

		url (str):
			URL associated with the current row.
	"""
	def __init__(self):
		self.size: int = 0
		"""Amount of processed elements."""

		self.prepare_data: int = None
		"""Defines the current data preparation mode."""

		self.infobox: dict = None
		"""Information extracted from the wiki infobox."""

		self.row: list = None
		"""Temporary row currently being processed."""

		self.is_d: bool = False
		"""Indicates whether the entry belongs to D format."""

		self.is_deck: bool = False
		"""Indicates whether the parser is processing decks."""

		self.obj: object = None
		"""Output model used to build parsed data."""

		self.card: list[str] = None
		"""Temporary card-related information."""

		self.rows: list[object] = []
		"""Accumulated list of constructed models."""

		self.links: dict = None
		"""Mapping between names and URLs."""

		self.is_duplicated: bool = None
		"""Indicates whether the current entry already exists."""

		self.id: int = None
		"""Internal incremental index."""

		self.url: str = None
		"""URL associated with the current row."""

class	CardFSM:
	def	__init__(self, fsm_context: FSMContext):
		self.fsm_context =	fsm_context
		self.context =		ParserContext()

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

	def __normalize_length(self):
		if (self.context.size < 6):
			self.context.row.insert(len(self.context.row), '')
		i = 0
		while (self.context.size != 6):
			try:
				if (self.context.row[i] == '' or
						self.context.row[i] == "V" or
						self.context.row[i] == "D" or
						self.context.row[i] == "DZ"):
					self.context.row.pop(i)
					i = 0
					self.context.size = len(self.context.row)
					continue
				i += 1
				self.context.size = len(self.context.row)
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
				"cards": 2
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
		nations = sum(
			1 for nation in self.context.card
			if (str(nation) in NATIONS)
		)

		if (self.state == ParserState.DUAL_CARD):
			pass
		if (self.context.size == 8):
			self.state = ParserState.DUAL_CARD
		elif (nations >= 2):
			self.state = ParserState.DUAL_NATION
		elif (self.fsm_context.main_category == "decks"):
			self.state = ParserState.DECK
		else:
			self.state = ParserState.SINGLE_CARD

		handler = self._dispatcher[self.state]
		if (handler["prepare"]):
			data = handler["prepare"](self.context.card)
		self.context.row = handler["parse"](data)
		self.context.prepare_data = handler["cards"]
		if (self.state != ParserState.DUAL_CARD):
			self.context.size = len(self.context.row)
			self.__normalize_length()
