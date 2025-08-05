import os
from config import MAX_CHARS

def get_file_content(working_directory, file_path):

	absworking_directory = os.path.abspath(working_directory)
	absjoined_path = os.path.abspath(os.path.join(working_directory, file_path))
	if not absjoined_path.startswith(absworking_directory):
		return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
	if not os.path.isfile(absjoined_path):
		return f'Error: File not found or is not a regular file: "{file_path}"'

	try:
		with open(absjoined_path, 'r') as f:
			content = f.read(MAX_CHARS + 1)
			if len(content) > MAX_CHARS:
				content = content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
		return content
	except Exception as e:
		return f'Error: {e}'
