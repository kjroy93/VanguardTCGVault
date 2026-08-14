# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    fsm.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/08 17:21:44 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 22:01:02 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import inspect
from enum 			import Enum, auto
from dataclasses	import dataclass, field
from typing 		import Awaitable, Callable

# Definitions
JSONType = dict[str]
type Action[C, D] = Callable[[C, D], None | Awaitable[None]]

class	InvalidTransition:
	pass

class	PipelineState(Enum):
	ENTRY_POINT				= auto()
	MAIN_CATEGORY_SELECTED	= auto()
	SUB_CATEGORY_SELECTED	= auto()
	QUERY_BUILT				= auto()
	SET_CONSULT				= auto()
	URL_PARSED				= auto()
	END						= auto()

class	PipelineEvent(Enum):
	SELECT_CATEGORY			= auto()
	SELECT_SUBCATEGORY		= auto()
	BUILD_QUERY				= auto()
	MAKE_CONSULT			= auto()
	CLEAN_RESULT			= auto()
	MAIN_ROUTINE			= auto()
	ERROR					= auto()

@dataclass
class	SetContext:
	category:			str				| None = None
	subcategory:		str				| None = None
	query_page:			str				| None = None
	query_parameters:	str				| None = None
	column:				str				| None = None
	tpl:				dict			| None = None
	response:			dict			| None = None
	api_result:			dict			| None = None
	links:				dict			| None = None
	infobox:			dict			| None = None
	crude_cards:		list			| None = None
	rows:				list[object]	| None = None
	is_d:				bool			| None = None
	is_deck:			bool			| None = None

@dataclass
class	StateMachine[S: Enum, E: Enum, C, D]:
	initial_state: S
	current_state: S = field(init=False)
	transitions: dict[tuple[S, E], tuple[S, Action[C, D]]] = field(
		default_factory=dict[tuple[S, E], tuple[S, Action[C, D]]]
	)

	def	__post_init__(self) -> None:
		self.current_state = self.initial_state
		
	def	add_transition(self, from_state: S, event: E, to_state: S, func: Action[C, D]) -> None:
		self.transitions[(from_state, event)] = (to_state, func)

	def	next_transition(self, state: S, event: E) -> tuple[S, Action[C, D]]:
		try:
			return (self.transitions[(state, event)])
		except KeyError as e:
			raise InvalidTransition(f"Cannot {event.name} when {state.name}") from e

	async def	handle(self, ctx: C, event: E, deps: D) -> S:
		next_state, action = self.next_transition(self.current_state, event)
		result = action(ctx, deps)
		if inspect.isawaitable(result):
			await result
		self.current_state = next_state
		return (self.current_state)
