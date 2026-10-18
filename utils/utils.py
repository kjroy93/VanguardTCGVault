# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/16 19:28:58 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
import random
import asyncio
import unicodedata
from html							import unescape

# Dependencies
from mwparserfromhell.nodes.extras	import Parameter
from routine.fsm					import SetContext

def	remove_from_list(sets: list, to_delete: list):
	return ([s for s in sets if not any(pattern in s for pattern in to_delete)])

def	construct_rules(rule: str):
	param = f"^{re.escape(rule)}"
	rules = [
		(r"^P Special", "V"),
		(r"^P&V", "V"),
		(r"^Special", "V"),
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
	x = random.randint(4, 6)
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
		text = text.replace('_', ' ')

	text = re.sub(r"\s+", " ", text)
	text = unescape(text)
	return (text.strip())

def dispatcher(set_ctx: SetContext):
	def	main_dispatcher() -> str | None:
		prefix = {
			"other": "List of "
		}
		return (prefix.get(
			set_ctx.category,
			"List of Cardfight!! Vanguard "
		))

	def sub_dispatcher() -> str | None:
		sub_dispatch = {
			"Unique Booster Sets": set_ctx.subcategory,
			"Monthly Bushiroad": set_ctx.subcategory
		}
		if (set_ctx.subcategory in sub_dispatch):
			return (sub_dispatch[set_ctx.subcategory])

	result = sub_dispatcher()

	if (result is not None):
		return (result)

	return (main_dispatcher() + set_ctx.subcategory)

def	make_custom_alphabet(page_titles: list[str]) -> dict[str, dict[str]]:
	page_titles_by_initial = {}
	for page_title in page_titles:
		normalized_page_title = clean_text(page_title)
		if (not normalized_page_title):
			continue
		letter = normalized_page_title[0]
		if (letter not in page_titles_by_initial):
			page_titles_by_initial[letter] = {}
		page_titles_by_initial[letter][normalized_page_title] = page_title
	return (page_titles_by_initial)

def	column_dispatcher(set_ctx: SetContext):
	dispatcher = {
		"table": ["Code", "Name", "Grade",
				"Faction", "FactionType", "Type",
				"Rarity", "Release", "URL", "SET_ID"],
		"deck": ["Code", "Name", "Grade",
		   		"Faction", "FactionType", "Type",
				"Amount", "Release", "URL", "SET_ID"]
	}
	table_kinds = {table_kind for table_kind, _ in set_ctx.card_entries}
	if (table_kinds == {"card", "deck"}):
		columns = dispatcher["table"].copy()
		columns.insert(columns.index("Rarity") + 1, "Amount")
		return (columns)
	if (table_kinds == {"deck"}):
		return (dispatcher["deck"])
	if (table_kinds == {"card"}):
		return (dispatcher["table"])
	if (set_ctx.is_deck):
		return (dispatcher.get("deck"))
	return (dispatcher.get("table"))
