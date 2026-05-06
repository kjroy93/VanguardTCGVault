# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    apu_builder.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:28:41 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:28:41 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from typing import Union, Literal

header = {
	"User-Agent": "VanguardScrapper/1.0 (Python; contact: kmarrero1993@gmail.com)"
}
first_param = {
	"action": "parse",
	"page": "List of Cardfight!! Vanguard Booster Sets",
	"format": "json"
}

def dict_construct(consult: Union[Literal["consult", "get"]], lst: list):
	if (consult == "consult"):
		return {
			i: {
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"titles": value,
			"rvprop": "content",
			"rvslots": "main"
		}
		for i, value in enumerate(lst)
	}
	else:
		return {
			value: {
				"action": "parse",
				"page": value,
				"format": "json"
			}
			for _, value in enumerate(lst)
		}
