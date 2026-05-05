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

from mwparserfromhell.nodes import Template

def	convert_to_str(element: Template):
	return (str(element.value).strip())

def	convert_to_int(element: str):
	if (element.isdigit()):
		return (int(element))
	raise ValueError

def normalize_length(data: list, lenght: int):
	i = 0
	while (lenght != 6):
		if (data[i] == ''):
			data.pop(i)
			i += 1
		i += 1
	return (data)

def	raw_table_data_prepare(template: list):
	data = []
	lst = normalize_length(template, len(template))
	for i in lst:
		raw_value = convert_to_str(i)
		try:
			value = convert_to_int(raw_value)
		except ValueError:
			value = raw_value
		if (value != None):
			data.append(value)
	return (data)
