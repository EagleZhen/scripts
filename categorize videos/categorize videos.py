import ez,os,json,shutil
from ez import pause,stop
from os.path import join

# stop(ez.get_info_path())
info_file_path = join(ez.get_info_path(),"List.json")
# stop(info_file_path)

with open(info_file_path,'r') as f:
	data = json.load(f)

source_path=data["source_path"]
destination_path=data["destination_path"]
file_list=os.listdir(source_path)

location_dict=data["aliases"]
# stop(location_dict)

change_list = [] # list of files to be moved and their corresponding destination path
planned_destinations = set()
for file in file_list:
	# assume the file name format is "<prefix> <friend> <original file name>"
	parts = file.split(maxsplit=2)
	if (len(parts)<3):
		print (f"Skipped \"{file}\" because it does not follow the naming convention.")
		continue
	prefix, friend, original_name = parts

	if (prefix in location_dict):
		final_destination_path = join(destination_path, location_dict[prefix])

		# play with friends
		if (friend=="F"):
			new_file = f"{prefix} {original_name}"
			final_destination_path = join(final_destination_path, "with friends")
		
		# single player
		elif (friend=="S"):
			new_file = f"{prefix} {original_name}"
		
		else:
			print (f"[!] \"{file}\" is not yet labelled.")
			continue
		
		source = join(source_path,file)
		dest = final_destination_path
		target = join(dest, new_file)
		target_key = os.path.normcase(os.path.abspath(target))
		if os.path.lexists(target):
			print(f'[!] Skipped "{file}": destination already exists: "{target}".')
			continue
		if target_key in planned_destinations:
			print(f'[!] Skipped "{file}": another file is already planned for "{target}".')
			continue
		planned_destinations.add(target_key)
		change_list.append((source,dest,file,new_file))
	else:
		print(f'[!] Skipped "{file}": unknown game tag "{prefix}". Add it to aliases in List.json.')

current_prefix = ""
for source,dest,old_file,new_file in change_list:
	# stop(source,dest)
	prefix = os.path.basename(source).split(maxsplit=2)[0]
	if (prefix != current_prefix):
		current_prefix = prefix
		print(f"=====================================\n{location_dict[current_prefix]}\n")
	print(f"\"{source}\" \n\tnew location: {join(dest, new_file)}")

if (len(change_list)==0):
	pause("No files to be moved.")
	stop()

choice = input("=====================================\nCorrect? (yes/no): ")
if (choice == "yes"):
	for source,dest,old_file,new_file in change_list:
		target = join(dest, new_file)
		# Recheck in case the destination appeared while awaiting confirmation.
		if os.path.lexists(target):
			print(f'[!] Skipped "{old_file}": destination already exists: "{target}".')
			continue
		os.makedirs(dest, exist_ok=True)
		shutil.move(source, target)
		print(f'Moved "{source}" to "{target}".')

pause("====================Done!====================\a")
