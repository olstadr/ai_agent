import os

def write_file(working_directory, file_path, content):

	absworking_directory = os.path.abspath(working_directory)
	absjoined_path = os.path.abspath(os.path.join(working_directory, file_path))

	if not absjoined_path.startswith(absworking_directory):
		return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

	try:
		os.makedirs(os.path.dirname(absjoined_path), exist_ok=True)
		with open(absjoined_path, 'w') as file:
			file.write(content)
			return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
	except Exception as e:
		return f'Error: {e}'
