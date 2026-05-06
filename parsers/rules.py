# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    rules.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/06 12:56:29 by marvin            #+#    #+#              #
#    Updated: 2026/05/06 12:56:29 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import re

def	construct_rules(rule: str):
	param = f"^{re.escape(rule)}"
	rules = [
		(r"^DZ", "DZ"),
		(r"^D", "D"),
		(r"^G", "G"),
		(r"^V", "V"),
		(param, "LB")
	]
	return (rules)
