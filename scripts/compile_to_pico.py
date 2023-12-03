import re
import os

read_dir = 'src/'
main_file = 'code.py'
output_file_path = '/dist/code.py'

# Get List Of Files To Compile
files = os.listdir(read_dir)
compilation_files = []
for filename in files:
  if filename.split('.')[-1] == 'py':
    compilation_files.append({
      'file': filename,
      'is_main': filename == main_file,
      'path': read_dir + filename,
      'content': '',
      'import_statements': []
    })

# Store File Contents
for f in compilation_files:
  with open(f['path'], 'r') as file:
    f['content'] = file.read()

# Get Import Statements
for f in compilation_files:
  matches = re.finditer(r'(?:import|from) +.+', f['content'], flags=re.MULTILINE | re.IGNORECASE)
  if matches:
    for match in matches:
      f['import_statements'].append(match.group())

for f in compilation_files:
  istatements = f['import_statements']
  output = {}
  for statement in istatements:
    words = statement.split(' ')
    if 'from' in words:
      lib = words[1]
      if lib not in output:
        output[lib] = []
      
      import_index = words.index('import') + 1
      imports = words[import_index:]
      for imp in imports:
        output[lib].append(imp)
    else:
      libs = [word.replace(',', '').strip() for word in words[1:]]
      for lib in libs:
        if lib not in output:
          output[lib] = []
  f['imports'] = output
    
print(compilation_files[1]['imports'])
