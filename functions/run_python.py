import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
	absworking_directory = os.path.abspath(working_directory)
	absjoined_path = os.path.abspath(os.path.join(working_directory, file_path))

	if not absjoined_path.startswith(absworking_directory):
		return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
	if not os.path.exists(absjoined_path):
		return f'Error: File "{file_path}" not found.'
	if not absjoined_path.endswith(".py"):
		return f'Error: "{file_path}" is not a Python file.'

	try:
		combined_list = ['python', absjoined_path] + args
		completed_process = subprocess.run(combined_list, cwd=absworking_directory, capture_output=True, timeout=30)
		stdout = completed_process.stdout
		stdout = stdout.decode().strip()
		stderr = completed_process.stderr
		stderr = stderr.decode().strip()
		returncode = completed_process.returncode

		final_return_line = []

		if not stdout == '':
			final_return_line.append(f'STDOUT: {stdout}')
		if not stderr == '':
			final_return_line.append(f'STDERR: {stderr}')
		if not returncode == 0:
			final_return_line.append(f'Process exited with code {returncode}')

		if final_return_line == []:
			return "No output produced"
		return "\n".join(final_return_line)

	except Exception as e:
		return f'Error: executing Python file: {e}'
