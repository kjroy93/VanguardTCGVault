# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    types.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/15 16:35:00 by kjroydev          #+#    #+#              #
#    Updated: 2026/10/18 03:23:26 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from typing	import Literal
from enum	import Enum, auto

type TableKind = Literal["card", "deck"]

class	MetadataType(Enum):
	DECK	= auto()
	SINGLE	= auto()
	DUAL	= auto()

class	CardType(Enum):
	SINGLE_CARD	= auto()
	DUAL_CARD	= auto()
	DUAL_NATION	= auto()
	PROMO		= auto()
	DECK		= auto()
