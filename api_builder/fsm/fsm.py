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

# Library
from api_builder.vanguard_api_build import JSONType

class	FSMContext:
	def __init__(self):
		self.reset()

	def	reset(self):
		self.data: dict = {}
		self.answer: str | None = None
		self.subcategory: str | None = None
		self.current_state: str | None = None
		self.main_category: str | None = None
		self.api_answer: JSONType | None = None

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

