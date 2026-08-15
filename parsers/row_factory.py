# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    row_factory.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:39:14 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/15 18:48:28 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from routine.fsm	import SetContext
from cards.fsm		import CardContext

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
		if (isinstance(row[3], list)):
			return (row[3])
		if (row[3] == '-'):
			return (["None"])
		return ([row[3]])

	@staticmethod
	def	prepare_grade(row: list):
		if (row[2] == '' or row[2] == '-'):
			row[2] = 0

	@staticmethod
	def	construct_decks(card_ctx: CardContext, set_ctx: SetContext) -> object:
		release = RowFactory.get_release(card_ctx.infobox)
		faction = RowFactory.prepare_faction(card_ctx.row)
		try:
			row = card_ctx.obj(
				Code =			card_ctx.row[0],
				Amount =		card_ctx.row[1],
				Name =			card_ctx.row[2],
				Grade = 		card_ctx.row[3],
				Faction =		faction,
				FactionType =	"Nation" if set_ctx.is_d else "Clan",
				Type = 			card_ctx.row[5],
				Release = 		release,
			)
			set_ctx.rows.append(row)
		except (IndexError, ValueError):
			row = card_ctx.obj(
				Code =			"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		release,
			)
			set_ctx.rows.append(row)

	@staticmethod
	def	construct_row(card_ctx: CardContext, set_ctx: SetContext) -> object:
		release = RowFactory.get_release(set_ctx.infobox)
		faction = RowFactory.prepare_faction(card_ctx.row)
		RowFactory.prepare_grade(card_ctx.row)
		print("DEBUG id")
		print("id:", card_ctx.id)

		id = int(card_ctx.id)

		print("id final:", repr(id))
		try:
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
		except (IndexError, ValueError):
			row = card_ctx.obj(
				Code =			"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		release,
				URL =			card_ctx.url,
				SET_ID = 		int(card_ctx.id)
			)
			set_ctx.rows.append(row)

	@staticmethod
	def	construct_rows(card_ctx: CardContext, set_ctx: SetContext):
		for i in range(len(card_ctx.row)):
			release = RowFactory.get_release(card_ctx.infobox)
			faction = RowFactory.prepare_faction(card_ctx.row[i])
			RowFactory.prepare_grade(card_ctx.row)
			try:
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
			except (IndexError, ValueError):
				row = card_ctx.obj(
					Code =			"None",
					Name =			"None",
					Grade =			0,
					Faction =		["None"],
					FactionType =	"None",
					Type = 			"None",
					Rarity = 		"None",
					Release = 		release,
					URL =			card_ctx.url,
					URL_ID = 		int(card_ctx.id)
				)
			set_ctx.rows.append(row)
			card_ctx.id += 1
