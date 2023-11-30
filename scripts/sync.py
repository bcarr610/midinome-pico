from datetime import datetime
import shutil
from pathlib import Path
import os

print('Starting')

board_drive = 'D:/'
board_ignore_paths = [
  '.fseventsd',
  'lib',
  '.metadata_never_index',
  '.Trashes',
  'boot_out.txt',
  'settings.toml'
]

local_sync_dir = 'src/'

def get_last_modified_time(file_path):
  last_m_time = os.path.getmtime(file_path)
  return last_m_time

def get_items_from_dir(dir_path):
  items = []
  dir_content = os.listdir(dir_path)
  for item in dir_content:
    if item != 'System Volume Information' and item not in board_ignore_paths:
      item_path = os.path.join(dir_path, item)
      if os.path.isfile(item_path):
        items.append({
          'file': item,
          'path': item_path.replace('\\', '/')
        })
      elif os.path.isdir(item_path):
        new_items = get_items_from_dir(item_path)
        items.extend(new_items)
  return items

local_dir = get_items_from_dir(local_sync_dir)
board_dir = get_items_from_dir(board_drive)

def find_in(item, arr):
  for i in range(len(arr)):
    arrItem = arr[i]['file']
    if item['file'] == arrItem:
      return arr[i]
  return False

# Remove All Files From Board that aren't in src
for item in board_dir:
  # print(item)
  should_remove = False
  found_in_local = find_in(item, local_dir)
  if found_in_local == False:
    print(f'Removing: {item}...')
    path = Path(item['path'])
    path.unlink()

# Update Files
for local_file in local_dir:
  found_file = find_in(local_file, board_dir)

  if found_file == False:
    # Create File
    pass
  else:
    last_modified_on_board = get_last_modified_time(found_file['path'])
    last_modified_on_local = get_last_modified_time(local_file['path'])
    if last_modified_on_local > last_modified_on_board:
      print(f'Updating {found_file["file"]}...')
      shutil.copy(local_file['path'], found_file['path'])
