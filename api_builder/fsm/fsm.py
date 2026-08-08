# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    fsm.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/08 17:21:44 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/08 20:36:34 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Library
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

JSONType = dict[str]
type Action[C] = Callable[[C], None]

class	ParseState(Enum):
	ENTRY_POINT				=	auto()
	SELECT_MAIN_CATEGORY	= 	auto()
	SELECT_SUBCATEGORY		=	auto()
	BUILD_QUERY				=	auto()
	FETCH					=	auto()
	PARSE					=	auto()
	SCRAP					=	auto()
	END						=	auto()

class	ParseEvent(Enum):
	CATEGORY_SELECTED		= auto()
	SUBCATEGORY_SELECTED	= auto()
	QUERY_BUILT				= auto()
	CLEAN_RESULT			= auto()
	MAIN_ROUTINE			= auto()
	ERROR					= auto()

@dataclass
class	StateMachine[S: Enum, E: Enum, C]:
	initial_state: S
	current_state: S = field(init=False)
	transitions: dict[tuple[S, E], tuple[S, Action[C]]] = field(
		default_factory=dict[tuple[S, E], tuple[S, Action[C]]]
	)

	def	__post_init__(self) -> None:
		self.current_state = self.initial_state
		
	def	add_transition(self, from_state: S, event: E, to_state: S, func: Action[C]) -> None:
		self.transitions[(from_state, event)] = (to_state, func)

	def	transition(self, event: E):
		key = (self.current_state, event)
	

@dataclass
class	ParseContext:
	category:			str			|	None = None
	column:				str			|	None = None
	subcategory:		str			|	None = None
	query_page:			str			|	None = None
	query_parameters:	str			|	None = None
	crude_data:			JSONType	|	None = None
	data:				JSONType	|	None = None

class	FSMConsults:
	def	__init__(self):
		self.reset()
	
	def reset(self):
		self.answer: str | None = None
		self.answer_lb : bool | None = None
		self.answer_ll : bool | None = None
		self.answer_g : bool | None = None
		self.answer_v : bool | None = None
		self.answer_d : bool | None = None
		self.answer_dz : bool | None = None
		self.lb: str | dict = None
		self.ll: str | dict = None
		self.g: str | dict = None
		self.v: str | dict = None
		self.d: str | dict = None
		self.dz: str | dict = None
		self.current_state: str | None = None

class	Consult(Enum):
	CHECK_DATABASE		=	auto()
	REQUIRE_DATABASE	=	auto()
	MAKE_CONSULT 		=	auto()
	READY				=	auto()
	STORE_INFO			=	auto()
	END					=	auto()
