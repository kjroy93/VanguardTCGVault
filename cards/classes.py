# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cards.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:43:54 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:43:54 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
from typing import Literal, Optional, Annotated, Union

# Dependencies
from pydantic import BaseModel, Field

class	ScrapCard(BaseModel):
	Code:			str
	Name:			str
	Grade:			int | None = None
	Faction:		list[str] | None = None
	FactionType:	str | None = None
	Type:			str | None = None
	Rarity:			str | None = None
	Release:		str | None = None
	URL:			str | int = None

class	ScrapDeck(BaseModel):
	Code:			str
	Amount:			Optional[int] = None
	Name:			str
	Grade:			Optional[int] = None
	Faction:		str
	FactionType:	str
	Type:			Optional[str] = None
	Release:		str
	URL:			str

class	Card(BaseModel):
	name:			str
	kaji:			Optional[str] = None
	kana:			Optional[str] = None
	phonetic:		Optional[str] = None
	korean:			Optional[str] = None
	thai:			Optional[str] = None
	italian:		Optional[str] = None
	card_type:		str
	grade:			Optional[int] = None
	skill:			Optional[str] = None
	power:			Optional[int] = None
	shield:			Optional[int] = None
	critical:		Optional[int] = None
	nation:			Optional[str] = None
	clan:			Optional[str] = None
	race:			Optional[str] = None
	valid_format:	Optional[str] = None
	card_set:		list[str] = Field(default_factory=list)
	card_flavor:	Optional[str] = None
	card_effect:	str
	tournament:		Optional[str] = None

class	Trigger(Card):
	card_type:		str = "trigger_unit"
	boost:			Optional[int] = None
	trigger_effect:	str

class	Order(Card):
	card_type:		str = "order"
	order_type:		str

class	NormalOrder(Order):
	order_type:		Literal["normal"]

class	BlitzOrder(Order):
	order_type:		Literal["blitz"]

CardUnion = Annotated[
	Union[Trigger, NormalOrder, BlitzOrder],
	Field(discriminator="card_type")
]
