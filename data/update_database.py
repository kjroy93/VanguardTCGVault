# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    update_database.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/14 19:40:18 by kmarrero          #+#    #+#              #
#    Updated: 2026/08/14 19:41:02 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Import
import json
import os

# Library
from utils.constants	import FILE, DATA_DIR

class	LinkStorage:
	def	__load_data(self):
		if (os.path.exists(FILE)):
			with open(FILE, "r", encoding="utf-8") as f:
				return (json.load(f))
		return ({})

	def	__init__(self):
		self._links = self.__load_data()

	def	__save_data(self):
		try:
			with open(FILE, "w", encoding="utf-8") as f:
				json.dump(self._links, f, indent=4, ensure_ascii=False)
		except FileNotFoundError as e:
			print(f'Error {e} detected, creating file to save urls')
			os.mkdir(DATA_DIR)
			with open("urls.json", "w") as f:
				json.dump(self._links, f, ident=4, ensure_ascii=False)

	def get_or_create(self, url: str, next_id: int) -> tuple[int, bool]:
		url = url.strip()

		if (url in self._links):
			return (self._links[url], False)

		self._links[url] = next_id
		self.__save_data()
		return (next_id, True)