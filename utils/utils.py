# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    utils.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: marvin <marvin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/05 15:23:17 by marvin            #+#    #+#              #
#    Updated: 2026/05/05 15:23:17 by marvin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

def remove_from_list(sets: list, to_delete: list):
	return ([s for s in sets if not any(pattern in s for pattern in to_delete)])