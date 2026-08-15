# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    types.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/15 16:35:00 by kjroydev          #+#    #+#              #
#    Updated: 2026/08/15 16:37:55 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from enum import Enum, auto

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
