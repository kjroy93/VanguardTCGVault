# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    normalizers.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:18:17 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:18:17 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Dependencies
from mwparserfromhell.nodes import Template

def	convert_to_str(element: Template):
	return (str(element.value).strip())

def	convert_to_int(element: str):
	if (element.isdigit()):
		return (int(element))
	raise ValueError

def normalize_length(data: list, size: int):
	i = 0
	lenght = len(data)
	while (lenght != size):
		if (data[i] == ''):
			data.pop(i)
			i += 1
		i += 1
		lenght = len(data)
	return (data)

def	raw_table_data_prepare(template: list, size: int):
	data = []
	lst = normalize_length(template, size)
	for i in lst:
		raw_value = convert_to_str(i)
		try:
			value = convert_to_int(raw_value)
		except ValueError:
			value = raw_value
		if (value != None):
			data.append(value)
	return (data)
