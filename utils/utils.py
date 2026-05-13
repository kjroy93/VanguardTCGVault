# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:23:17 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
import random
import asyncio

# Dependencies
from mwparserfromhell.nodes.extras import Parameter

def remove_from_list(sets: list, to_delete: list):
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
	x = random.randint(2, 6)
	await asyncio.sleep(x)