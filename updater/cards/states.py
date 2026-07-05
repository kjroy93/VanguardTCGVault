# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    states.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/12 18:00:42 by marvin            #+#    #+#              #
#    Updated: 2026/05/12 18:00:42 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from enum import Enum, auto

class	ParserState(Enum):
	START		=	auto()
	SINGLE_CARD =	auto()
	DUAL_NATION	=	auto()
	DUAL_CARD	=	auto()
	DECK		=	auto()
	PROMO		=	auto()
	END			=	auto()