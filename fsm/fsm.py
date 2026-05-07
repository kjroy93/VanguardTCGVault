# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    fsm.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/07 13:21:28 by marvin            #+#    #+#              #
#    Updated: 2026/05/07 13:21:28 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#Import 
from enum import Enum, auto

class	State(Enum):
	ENTRY_POINT =			auto()
	SELECT_MAIN_CATEGORY = 	auto()
	SELECT_SUBCATEGORY =	auto()
	BUILD_QUERY =			auto()
	FETCH =					auto()
	PROCESS =				auto()
	END =					auto()
	ERROR =					auto()

class FSMContext:
	def __init__(self):
		self.reset()
	
	def	reset(self):
		self.data: dict = {}
		self.query: str | None = None
		self.answer: str | None = None
		self.results: list | None = None
		self.subcategory: str | None = None
		self.current_state: str | None = None
		self.main_category: str | None = None