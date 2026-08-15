# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/15 23:44:13 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
import random
import asyncio
import unicodedata

# Dependencies
from mwparserfromhell.nodes.extras	import Parameter
from routine.fsm					import SetContext

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
		text = text.replace('_', ' ')

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

def	make_custom_alphabet(crude_links: list[str]):
	alphabet = {}
	for link in crude_links:
		clean_link = clean_text(link)
		if (not clean_link):
			continue
		letter = clean_link[0]
		if (letter not in alphabet):
			alphabet[letter] = {}
		alphabet[letter][clean_link] = link
	return (alphabet)