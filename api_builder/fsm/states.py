# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    states.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 10:57:34 by marvin            #+#    #+#              #
#    Updated: 2026/05/08 10:57:34 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from enum import Enum, auto

class	State(Enum):
	ENTRY_POINT				=	auto()
	SELECT_MAIN_CATEGORY	= 	auto()
	SELECT_SUBCATEGORY		=	auto()
	BUILD_QUERY				=	auto()
	FETCH					=	auto()
	PARSE					=	auto()
	END						=	auto()
	ERROR					=	auto()

class	Consult(Enum):
	CHECK_DATABASE		=	auto()
	REQUIRE_DATABASE	=	auto()
	MAKE_CONSULT 		=	auto()
	READY				=	auto()
	STORE_INFO			=	auto()
	END					=	auto()
