# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/13 17:10:20 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
import random
import asyncio
import unicodedata

# Dependencies
from mwparserfromhell.nodes.extras	import Parameter
from scrapper.fsm					import ParseContext as Context

def	remove_from_list(sets: list, to_delete: list):
	return ([s for s in sets if not any(pattern in s for pattern in to_delete)])

def	construct_rules(rule: str):
	param = f"^{re.escape(rule)}"
	rules = [
		(r"^DZ", "DZ"),
		(r"^D", "D"),
		(r"^G", "G"),
		(r"^V", "V"),
		(r"^P", "LB"),
		(param, "LB")
	]
	return (rules)

def	convert_to_str(element: Parameter):
	return (str(element.value).strip())

def	convert_to_int(element: str):
	if (element.isdigit()):
		return (int(element))
	raise ValueError

async def	smart_sleep():
	x = random.randint(4, 8)
	await asyncio.sleep(x)

def clean_text(text: str) -> str:
	text = unicodedata.normalize("NFKC", text)

	invisible_chars = [
		"\u200e",
		"\u200f",
		"\u200b",
		"\ufeff"
	]

	for char in invisible_chars:
		text = text.replace(char, "")

	return (text.strip())

def dispatcher(ctx: Context):
	def	main_dispatcher() -> str | None:
		prefix = {
			"other": "List of "
		}
		return (prefix.get(
			ctx.category,
			"List of Cardfight!! Vanguard "
		))

	def sub_dispatcher() -> str | None:
		sub_dispatch = {
			"Unique Booster Sets": ctx.subcategory,
			"Monthly Bushiroad": ctx.subcategory
		}
		if (ctx.subcategory in sub_dispatch):
			return (sub_dispatch[ctx.subcategory])

	result = sub_dispatcher()

	if (result is not None):
		return (result)

	return (main_dispatcher() + ctx.subcategory)