import os
import sys

def get_files_info(working_directory, directory="."):
	"""
	Retrieves formatted information about files and directories within a specified path.

	This function ensures that only paths within the designated working_directory are accessed, providing a secure boundary for operations.

	Args:
		working_directory (str): The absolute path to the permitted working directory. All file operations are restricted to this directory.

		directory (str, optional): A relative path within the working_directory to list. Defaults to ".", meaning the working_directory itself.

	Returns:
		str: A multi-line string detailing the contents of the specified directory in the format "- name: file_size=X bytes, is_dir=Y". 
			Returns an error string (prefixed with "Error:") if:
				- The requested directory is outside the working_directory.
				- The requested path is not a directory.
				- Any OS-related error occurs during the file system operations (e.g., permissions).
	"""
	absworking_directory = os.path.abspath(working_directory)
	joined_path = os.path.join(working_directory, directory)

	if not os.path.abspath(joined_path).startswith(absworking_directory):
		return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
	if not os.path.isdir(joined_path):
		return f'Error: "{directory}" is not a directory'

	try:
		directory_contents = []
		for name in os.listdir(joined_path):
			item_path = os.path.join(joined_path, name)
			directory_contents.append(f"- {name}: file_size={os.path.getsize(item_path)}, is_dir={os.path.isdir(item_path)}")
		return "\n".join(directory_contents)
	except Exception as e:
		return f'Error: {e}'
