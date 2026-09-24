import ez,os,json
from ez import pause,stop,move_file,rename_file
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
for file in file_list:
	# assume the file name format is "<prefix> <friend> <original file name>"
	if (len(file.split(' '))<3):
		print (f"Skipped \"{file}\" because it does not follow the naming convention.")
		continue
	prefix = file.split(' ')[0] # the game alias
	friend = file.split(' ')[1] # whether play with friends or single player

	if (prefix in location_dict):
		final_destination_path = join(destination_path, location_dict[prefix])

		# single player
		if (friend=="F"):
			new_file = file.replace("F ","")
			final_destination_path = join(final_destination_path, "with friends")
		
		# play with friends
		elif (friend=="S"):
			new_file = file.replace("S ","")
		
		else:
			print (f"[!] \"{file}\" is not yet labelled.")
			continue
		
		source = join(source_path,file)
		dest = final_destination_path
		change_list.append((source,dest,file,new_file))
	else:
		print(f'[!] Skipped "{file}": unknown game tag "{prefix}". Add it to aliases in List.json.')

current_prefix = ""
for source,dest,old_file,new_file in change_list:
	# stop(source,dest)
	prefix = os.path.basename(source).split(' ')[0]
	if (prefix != current_prefix):
		current_prefix = prefix
		print(f"=====================================\n{location_dict[current_prefix]}\n")
	print(f"\"{source}\" \n\tnew location: {dest}")

if (len(change_list)==0):
	pause("No files to be moved.")
	stop()

choice = input("=====================================\nCorrect? (yes/no): ")
if (choice == "yes"):
	# update the progress bar whenever a file is moved
	for source,dest,old_file,new_file in change_list:
		# print(join(dest,old_file), join(dest, new_file))
		move_file(source, dest)
		rename_file(join(dest,old_file), join(dest, new_file))

pause("====================Done!====================\a")
