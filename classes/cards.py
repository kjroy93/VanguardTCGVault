# Import
from typing import Literal, Optional

# Dependencies
from pydantic import BaseModel, Field

class	ScrapCard(BaseModel):
	card_nro:		str
	name:			str
	grade:			Optional[int] = None
	nation:			str
	card_type:		str | None = None
	rarity:			str
	release:		str

class	Card(BaseModel):
	name:			str
	kana:			Optional[str] = None
	phonetic:		Optional[str] = None
	thai:			Optional[str] = None
	card_type:		str
	grade:			Optional[int] = None
	skill:			Optional[str] = None
	power:			Optional[int] = None
	shield:			Optional[int] = None
	critical:		Optional[int] = None
	nation:			Optional[str] = None
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
