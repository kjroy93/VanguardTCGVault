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
from pathlib			import Path

# Library
from routine.fsm		import SetContext
from utils.constants	import SET_PATHS, DB_FOLDER

def	get_duplicate_path(path: Path) -> Path:
	if not path.exists():
		return path
	
	stem = path.stem
	suffix = path.suffix
	parent = path.parent
	i = 1
	while True:
		new_path = parent / f"{stem}_{i}{suffix}"
		if (not new_path.exists()):
			return new_path
		i += 1

def build_set_path(category: str,
				set_type: str,
				block: str,
				set_number: int) -> Path:
	info = SET_PATHS[category][set_type]
	filename = (
		f"{block.lower()}_{set_number:02}.parquet"
	)
	path = (
		DB_FOLDER
		/ info["folder"]
		/ block.lower()
		/ filename
	)
	return (path)

def	set_exists(set_ctx: SetContext, block: str, set_number: int) -> bool:
	set_type = set_ctx.subcategory.strip().lower().split()[0]
	config = SET_PATHS.get(set_ctx.category, {}).get(set_type)
	if (config is None):
		return (False)
	path: Path = (
		DB_FOLDER
		/ config["folder"]
		/ block.lower()
		/ f"{block.lower()}_{set_number + 1:02d}.parquet"
	)
	return (path.exists())
