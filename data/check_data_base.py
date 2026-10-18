# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    check_data_base.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kjroydev <kjroydev@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 17:56:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/16 15:55:00 by kjroydev         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
import re
from pathlib			import Path

# Library
from routine.fsm		import SetContext
from utils.constants	import SET_PATHS, DB_FOLDER

def build_set_path(set_ctx: SetContext, block: str) -> Path:
	set_type = set_ctx.subcategory.strip().lower().split()[0]
	info = SET_PATHS[set_ctx.category][set_type]
	set_code = (set_ctx.set_code or "").strip().upper()
	if (re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", set_code) is None):
		raise ValueError(f"Invalid or missing set code: {set_ctx.set_code!r}")
	filename = f"{set_code}.parquet"
	path = (
		DB_FOLDER
		/ info["folder"]
		/ block.lower()
		/ filename
	)
	return (path)

def	set_exists(set_ctx: SetContext, block: str) -> bool:
	return build_set_path(set_ctx, block).is_file()
