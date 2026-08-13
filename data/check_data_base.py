# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    check_data_base.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kmarrero <kmarrero@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/08 17:56:17 by marvin            #+#    #+#              #
#    Updated: 2026/08/13 17:43:58 by kmarrero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# Imports
from pathlib			import Path

# Library
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
		if not new_path.exists():
			return new_path
		i += 1

def build_set_path(category: str,
				set_type: str,
				block: str,
				set_number: int) -> Path:
	info = SET_PATHS[category][set_type]
	filename = (
		f"{info['prefix']}_{set_number:02}.parquet"
	)
	path = (
		DB_FOLDER
		/ info["folder"]
		/ block.lower()
		/ filename
	)
	return (path)

# def check_database(context: FSMContext,
# 				   consult: FSMConsults,
# 				   classifier: VanguardClassifier,
# 				   storage: VanguardStorage) -> bool:
# 	category = context.answer
# 	if category not in SET_PATHS:
# 		return False
# 	for block in VALID_DATABASES:
# 		db = getattr(storage, block.lower())
# 		if not db:
# 			continue
# 		set_number = classifier.obtain_set_number(db[0])
# 		path = build_set_path(
# 			category=category,
# 			set_type="main",
# 			block=block,
# 			set_number=set_number
# 		)
# 		if path.exists():
# 			print(
# 				f"The database {path.name} needs an update? "
# 				"[y]es | [n]o"
# 			)
# 			user_i = input("> ").strip().lower()
# 			while user_i not in ("y", "n"):
# 				print("Invalid Input")
# 				user_i = input("> ").strip().lower()
# 			if user_i == "y":
# 				setattr(
# 					consult,
# 					"answer_" + block.lower(),
# 					True
# 				)
# 		else:
# 			setattr(
# 				consult,
# 				"answer_" + block.lower(),
# 				True
# 			)

# 	return True

# def	consult_routine(fsm: FSMConsults, parser: VanguardParser, storage: VanguardStorage):
# 	for block in VALID_DATABASES:
# 		if (fsm.current_state != Consult.MAKE_CONSULT):
# 			if (not check_database(block)):
# 				print(f"No data for {block}")
# 				request = parser.make_consults(getattr(storage, block.lower()))
# 				setattr(fsm, block.lower(), request)
# 			else:
# 				print("Do you wish to update this data? [y]es | [n]o")
# 				user_input = input("> ").strip().lower()
# 				if (user_input in ("y", "yes")):
# 					fsm.current_state = Consult.MAKE_CONSULT
# 				else:
# 					continue

# 	for block in VALID_DATABASES:
# 		print(block)
# 		result = consult_routine(parser, storage, block)
# 		setattr(fsm, block.lower(), result)
# 	fsm.current_state = Consult.READY
# 	return (fsm.current_state)
