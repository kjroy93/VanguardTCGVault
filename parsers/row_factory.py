# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    row_factory.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:39:14 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 19:39:45 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from scrapper.fsm	import PipelineContext as Context

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
	def	construct_decks(ctx: Context) -> object:
		release = RowFactory.get_release(ctx.infobox)
		faction = RowFactory.prepare_faction(ctx.row)
		try:
			row = ctx.obj(
				Code =			ctx.row[0],
				Amount =		ctx.row[1],
				Name =			ctx.row[2],
				Grade = 		ctx.row[3],
				Faction =		faction,
				FactionType =	"Nation" if ctx.is_d else "Clan",
				Type = 			ctx.row[5],
				Release = 		release,
			)
			ctx.rows.append(row)
		except (IndexError, ValueError):
			row = ctx.obj(
				Code =			"None",
				Amount =		"None",
				Name =			"None",
				Grade = 		0,
				Faction =		"None",
				FactionType =	"None",
				Type = 			"None",
				Release = 		release,
			)
			ctx.rows.append(row)

	@staticmethod
	def	construct_row(ctx: Context) -> object:
		release = RowFactory.get_release(ctx.infobox)
		faction = RowFactory.prepare_faction(ctx.row)
		RowFactory.prepare_grade(ctx.row)
		try:
			row = ctx.obj(
				Code =			ctx.row[0],
				Name =			ctx.row[1],
				Grade =			ctx.row[2],
				Faction =		faction,
				FactionType =	"Nation" if ctx.is_d else "Clan",
				Type = 			ctx.row[4],
				Rarity = 		ctx.row[5],
				Release = 		release,
				URL = 			ctx.url,
				SET_ID =		int(ctx.id)
			)
			ctx.rows.append(row)
		except (IndexError, ValueError):
			row = ctx.obj(
				Code =			"None",
				Name =			"None",
				Grade =			0,
				Faction =		["None"],
				FactionType =	"None",
				Type = 			"None",
				Rarity = 		"None",
				Release = 		release,
				URL =			ctx.url,
				SET_ID = 		int(ctx.id)
			)
			ctx.rows.append(row)

	@staticmethod
	def	construct_rows(ctx: Context):
		for i in range(len(ctx.row)):
			release = RowFactory.get_release(ctx.infobox)
			faction = RowFactory.prepare_faction(ctx.row[i])
			RowFactory.prepare_grade(ctx.row)
			try:
				row = ctx.obj(
					Code =			ctx.row[i][0],
					Name =			ctx.row[i][1],
					Grade =			ctx.row[i][2],
					Faction =		faction,
					FactionType =	"Nation" if ctx.is_d else "Clan",
					Type = 			ctx.row[i][4],
					Rarity = 		ctx.row[i][5],
					Release = 		release,
					URL = 			ctx.url,
					URL_ID =		int(ctx.id)
				)
			except (IndexError, ValueError):
				row = ctx.obj(
					Code =			"None",
					Name =			"None",
					Grade =			0,
					Faction =		["None"],
					FactionType =	"None",
					Type = 			"None",
					Rarity = 		"None",
					Release = 		release,
					URL =			ctx.url,
					URL_ID = 		int(ctx.id)
				)
			ctx.rows.append(row)
			ctx.id += 1