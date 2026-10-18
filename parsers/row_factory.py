# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    row_factory.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:39:14 by kmarrero          #+#    #+#              #
#    Updated: 2026/10/18 02:48:32 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from routine.fsm		import SetContext
from cards.fsm			import CardContext
from utils.constants	import REQUIRED_FIELDS

class	RowFactory:
	@staticmethod
	def	get_release(info: dict) -> str:
		return (
			info.get("release date")
			or info.get("release date:")
			or "Unknown"
		)

	@staticmethod
	def	prepare_faction(row: list):
		faction = row[3]
		if (faction is None):
			return (None)
		if (isinstance(faction, list)):
			return (faction)
		return ([faction])

	@staticmethod
	def	prepare_grade(row: list):
		if (row[2] == '' or row[2] == '-'):
			row[2] = None

	@staticmethod
	def	_validate_context(card_ctx: CardContext, set_ctx: SetContext):
		if (card_ctx.row is None):
			raise (ValueError(f"Card row is None: {card_ctx.card}"))
		if (set_ctx.infobox is None):
			raise (ValueError(f"Infobox is None: {card_ctx.card}"))
		if (card_ctx.url is None):
			raise (ValueError(f"Card URL is None"))
		if (card_ctx.id is None):
			raise (ValueError(f"Card ID is None: {card_ctx.card}"))

	@staticmethod
	def	_validate_row(row: list, card: str):
		for index, field in REQUIRED_FIELDS.items():
			if (index >= len(row)):
				raise (IndexError(
					f"Missing field {field} "
					f"(index {index}) in {card}")
				)

			if (field not in ("Grade", "Type") and row[index] is None):
				raise(ValueError(f"{field} is None in {card}"))

	@staticmethod
	def	construct_decks(card_ctx: CardContext, set_ctx: SetContext) -> object:
		release = RowFactory.get_release(set_ctx.infobox)
		faction = RowFactory.prepare_faction(card_ctx.row)
		RowFactory.prepare_grade(card_ctx.row)
		row = card_ctx.obj(
			Code =			card_ctx.row[0],
			Name =			card_ctx.row[1],
			Grade = 		card_ctx.row[2],
			Faction =		faction,
			FactionType =	"Nation" if set_ctx.is_d else "Clan",
			Type = 			card_ctx.row[4],
			Amount =		card_ctx.row[5],
			Release = 		release,
			URL =			card_ctx.url if card_ctx.already_scraped == False else "Reprint",
			SET_ID =		int(card_ctx.id)
		)
		set_ctx.rows.append(row)

	@staticmethod
	def	construct_row(card_ctx: CardContext, set_ctx: SetContext) -> object:
		RowFactory._validate_context(card_ctx, set_ctx)
		RowFactory._validate_row(
			card_ctx.row,
			card_ctx.card
		)
		release = RowFactory.get_release(set_ctx.infobox)
		faction = RowFactory.prepare_faction(card_ctx.row)
		RowFactory.prepare_grade(card_ctx.row)
		row = card_ctx.obj(
			Code =			card_ctx.row[0],
			Name =			card_ctx.row[1],
			Grade =			card_ctx.row[2],
			Faction =		faction,
			FactionType =	"Nation" if set_ctx.is_d else "Clan",
			Type = 			card_ctx.row[4],
			Rarity = 		card_ctx.row[5],
			Release = 		release,
			URL = 			card_ctx.url if card_ctx.already_scraped == False else "Reprint",
			SET_ID =		int(card_ctx.id)
		)
		set_ctx.rows.append(row)

	@staticmethod
	def	construct_rows(card_ctx: CardContext, set_ctx: SetContext):
		RowFactory._validate_context(card_ctx, set_ctx)
		for i in range(len(card_ctx.row)):
			RowFactory._validate_row(
				card_ctx.row[i],
				card_ctx.card
			)
			release = RowFactory.get_release(set_ctx.infobox)
			faction = RowFactory.prepare_faction(card_ctx.row[i])
			RowFactory.prepare_grade(card_ctx.row[i])
			row = card_ctx.obj(
				Code =			card_ctx.row[i][0],
				Name =			card_ctx.row[i][1],
				Grade =			card_ctx.row[i][2],
				Faction =		faction,
				FactionType =	"Nation" if set_ctx.is_d else "Clan",
				Type = 			card_ctx.row[i][4],
				Rarity = 		card_ctx.row[i][5],
				Release = 		release,
				URL = 			card_ctx.url,
				URL_ID =		int(card_ctx.id)
			)
			set_ctx.rows.append(row)
			card_ctx.id += 1
