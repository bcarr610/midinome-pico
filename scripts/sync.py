from datetime import datetime
import shutil
import os

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
  return datetime.fromtimestamp(last_m_time)

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

print('Local')
print(local_dir)
print('Board')
print(board_dir)

# Remove All Files From Board that aren't in src
for item in board_dir:
  
