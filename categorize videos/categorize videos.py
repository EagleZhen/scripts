import ez,os,json,shutil
from ez import pause,stop
from os.path import join

def section(title):
	print(f"\n--- {title} ---")

def show_groups(title, groups):
	if not groups:
		return
	section(title)
	for reason, entries in groups.items():
		print(f"  {'-' * 68}")
		print(f"  {reason} ({len(entries)}):")
		for filename, detail in entries:
			print(f"    {filename}\n      {detail}")

def show_summary(status, moved, skipped, failed, cancelled=0):
	counts = f"Moved: {moved}   Skipped: {skipped}   Failed: {failed}"
	if cancelled:
		counts += f"   Cancelled: {cancelled}"
	print(f"\n{status}. {counts}")

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
skipped_groups = {}

def record_skip(reason, filename, detail):
	skipped_groups.setdefault(reason, []).append((filename, detail))

for file in file_list:
	source = join(source_path, file)
	if os.path.isdir(source):
		record_skip("Directories", file, "Entry is a directory.")
		continue
	# assume the file name format is "<prefix> <friend> <original file name>"
	parts = file.split(maxsplit=2)
	if (len(parts)<3):
		record_skip("Invalid filenames", file, 'Expected "<game tag> <F/S> <original filename>".')
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
			record_skip("Invalid play modes", file, f'Found "{friend}"; expected F (with friends) or S (single player).')
			continue
		
		dest = final_destination_path
		target = join(dest, new_file)
		target_key = os.path.normcase(os.path.abspath(target))
		if os.path.lexists(target):
			record_skip("Existing destinations", file, f'Destination already exists: {target}')
			continue
		if target_key in planned_destinations:
			record_skip("Duplicate destinations in this batch", file, f'Another file is already planned for: {target}')
			continue
		planned_destinations.add(target_key)
		change_list.append((source,dest,file,new_file))
	else:
		record_skip("Unknown game tags", file, f'Add "{prefix}" to aliases in List.json.')

show_groups("SKIPPED ENTRIES - BY REASON", skipped_groups)

section("MOVE PREVIEW")
print(f"  Source : {source_path}\n  Root   : {destination_path}")
preview_groups = {}
for source,dest,old_file,new_file in change_list:
	preview_groups.setdefault(dest, []).append((old_file, new_file))
if not preview_groups:
	print("  No files ready to move.")
for dest, entries in preview_groups.items():
	print(f"  Destination: {dest} ({len(entries)} files)")
	for old_file, new_file in entries:
		print(f"    {old_file} -> {new_file}")

skipped_count = len(file_list) - len(change_list)
moved_count = 0
failed_count = 0

if (len(change_list)==0):
	show_summary("Nothing to move", 0, skipped_count, 0)
	pause()
	stop()

print(f"\nReady: {len(change_list)}   Skipped: {skipped_count}")
choice = input('Move these files? Type "yes" to proceed, or press Enter to cancel: ').strip().lower()
if (choice == "yes"):
	section("MOVING FILES")
	move_issues = {}
	for index, (source,dest,old_file,new_file) in enumerate(change_list, start=1):
		target = join(dest, new_file)
		# Recheck in case the destination appeared while awaiting confirmation.
		if os.path.lexists(target):
			print(f"  [{index}/{len(change_list)}] SKIPPED  {old_file}")
			move_issues.setdefault("Destinations that appeared after preview", []).append((old_file, f'Destination already exists: {target}'))
			skipped_count += 1
			continue
		try:
			os.makedirs(dest, exist_ok=True)
			shutil.move(source, target)
		except (OSError, shutil.Error) as error:
			failed_count += 1
			print(f"  [{index}/{len(change_list)}] FAILED   {old_file}")
			move_issues.setdefault("Move failures", []).append((source, f'Target: {target}; error: {error}'))
			continue
		moved_count += 1
		print(f"  [{index}/{len(change_list)}] MOVED    {old_file}")
	if move_issues:
		show_groups("MOVE ISSUES - BY REASON", move_issues)
	show_summary("Finished with failures" if failed_count else "Finished", moved_count, skipped_count, failed_count)
	pause("\a")
else:
	show_summary("Cancelled", 0, skipped_count, 0, len(change_list))
	pause()
