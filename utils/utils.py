# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/10 20:11:52 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
import random
import asyncio
import unicodedata

# Dependencies
from mwparserfromhell.nodes.extras import Parameter

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

