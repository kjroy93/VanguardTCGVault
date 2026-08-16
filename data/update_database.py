# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    update_database.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:40:18 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/16 16:00:48 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import json

# Library
from utils.constants	import FILE

class	LinkStorage:
	def __load_data(self):
		if (FILE.exists()):
			with FILE.open("r", encoding="utf-8") as f:
				return json.load(f)
		return ({})

	def	__init__(self):
		self._links = self.__load_data()

	def	__save_data(self):
		FILE.parent.mkdir(parents=True, exist_ok=True)
		with FILE.open("w", encoding="utf-8") as f:
			json.dump(
				self._links,
				f,
				indent=4,
				ensure_ascii=False
			)

	def get_or_create(self, url: str, next_id: int) -> tuple[int, bool]:
		url = url.strip()

		if (url in self._links):
			return (self._links[url], False)

		self._links[url] = next_id
		self.__save_data()
		return (next_id, True)
