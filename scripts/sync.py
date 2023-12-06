from typing import Optional, List
from datetime import datetime
import shutil
from pathlib import Path
import os

print('Syncing...')

board_drive = 'D:'
board_ignore_paths = [
  '.fseventsd',
  'lib',
  '.metadata_never_index',
  '.Trashes',
  'boot_out.txt',
  'settings.toml',
  'user-config.json'
]

local_sync_dir = 'src'

def get_last_modified_time(file_path: str):
  last_m_time = os.path.getmtime(file_path)
  return last_m_time

def get_items_from_dir(dir_path: str):
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

def copy_item(from_path: str, to_path: Optional[str] = None):
  from_path = from_path.replace('\\', '/')
  to_path = to_path.replace('\\', '/') if to_path else None

  print(from_path)
  print(to_path)
  
  if to_path:
    print(f'Copying {from_path} to {to_path}...')
    shutil.copyfile(from_path, to_path)
  else:
    creation_list = from_path.split('/')

    if 'src' in creation_list:
      start_index = creation_list.index('src')
      del creation_list[:start_index + 1]

    current_path = board_drive

    for index, pth in enumerate(creation_list):
      current_path = current_path + '/' + pth
      if index == len(creation_list) - 1:
        print(f'Copying {from_path} to {current_path}...')
        shutil.copyfile(from_path, current_path)
        break
      else:
        if not os.path.exists(current_path):
          print(f'Making Dir: {current_path}...')
          os.mkdir(current_path)
    
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
  should_remove = False
  found_in_local = find_in(item, local_dir)
  if found_in_local == False:
    print(f'Removing: {item}...')
    # TODO Check if directory is emtpy and remove directory and parent directories if all empty
    path = Path(item['path'])
    path.unlink()

# Update Files
for local_file in local_dir:
  found_file = find_in(local_file, board_dir)

  if found_file == False:
    copy_item(local_file['path'])
    # shutil.copyfile(local_file['path'])
    pass
  else:
    last_modified_on_board = get_last_modified_time(found_file['path'])
    last_modified_on_local = get_last_modified_time(local_file['path'])
    if last_modified_on_local > last_modified_on_board:
      print(f'Updating {found_file["file"]}...')
      copy_item(local_file['path'], found_file['path'])

copy_item('.\\user-config.json', 'D:/user-config.json')