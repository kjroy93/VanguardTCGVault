# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    fsm.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/12 17:52:03 by marvin            #+#    #+#              #
#    Updated: 2026/08/14 19:36:50 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from enum						import Enum, auto
from dataclasses				import dataclass, field
from typing						import Callable

# Dependencies
from mwparserfromhell.wikicode	import Wikicode

# Library
from utils.constants			import NATIONS

# Definitions
type Action[C] = Callable[[C], None]
class	InvalidTransition:
	pass

@dataclass
class	CardContext:
	pass
	
class	CardState(Enum):
	ENTRY_POINT	= auto()
	CARD_PARSER = auto()
	DATA_CHECK	= auto()
	SAVE_DATA	= auto()
	MAKE_JSON	= auto()
	END			= auto()
	

class	CardEvent(Enum):
	API_CALL		= auto()
	PARSER			= auto()
	CARD_CHECKER	= auto()
	DATAFRAME		= auto()
	JSON			= auto()
	ERROR			= auto()

@dataclass
class	CardStateMachine[S: Enum, E: Enum, C]:
	initial_state: S
	current_state: S = field(init=False)
	transitions: dict[tuple[S, E], tuple[S, Action[C]]] = field(
		default_factory=dict[tuple[S, E], tuple[S, Action[C]]]
	)

	def	__post_init__(self):
		self.current_state = self.initial_state

	def	add_transitions(self, from_state: S, event: E, to_state: S, func: Action[C]):
		self.transitions[(from_state, event)] = (to_state, func)

	def	next_transition(self, state: S, event: E) -> tuple[S, Action[C]]:
		try:
			return (self.transitions[(state, event)])
		except KeyError as e:
			raise InvalidTransition(f"Cannot {event.name} when {state.name}") from e

	def	handle(self, ctx: C, state: S, event: E) -> S:
		next_state, action = self.next_transition(state, event)
		action(ctx)
		return (next_state)
