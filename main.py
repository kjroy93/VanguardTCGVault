from typing import Union, Annotated

# Dependencie
from pydantic import BaseModel, Field

# Library
from classes.cards import Trigger, NormalOrder, BlitzOrder

# Params
header = {
	"User-Agent": "VanguardScrapper/1.0 (Python; contact: kmarrero1993@gmail.com)"
}
params = {
	"action": "query",
	"format": "json",
	"prop": "revisions",
	"title": url,
	"rvprop": "content",
	"rvslots": "main"
}
params_for_urls = {
	"action": "parse",
	"page": "List_of_Cardfight!!_Vanguard_Booster_Sets",
	"format": "json"
}
rules = [
	(r"^DZ", "DZ"),
	(r"^D", "D"),
	(r"^G", "G"),
	(r"^V", "V"),
	(r"^Booster", "LB"),
]

CardUnion = Annotated[
	Union[Trigger, NormalOrder, BlitzOrder],
	Field(discriminator="card_type")
]
