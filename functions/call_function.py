import os
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

"""
Function calling utilities for the LLM agent.

This module handles the execution of functions requested by the LLM,
including file operations and Python script execution.
"""

def call_function(function_call_part, verbose=False):
	"""
	Execute a function call requested by the LLM and return the result.

	Args:
		function_call_part (types.FunctionCall): The function call information from the LLM,
			containing the function name and arguments.
		verbose (bool, optional): If True, prints detailed function call information.
			If False, prints only the function name. Defaults to False.

	Returns:
		types.Content: A Content object with role "tool" containing either:
		- Success: {"result": function_return_value}
		- Error: {"error": "Unknown function: function_name"}
	Note:
		Automatically adds "working_directory": "./calculator" to all function calls.
	"""

	if verbose:
		print(f'Calling function: {function_call_part.name}({function_call_part.args}')
	else:
		print(f" - Calling function: {function_call_part.name}")

	functions_dict = {
		"get_files_info": get_files_info,
		"get_file_content": get_file_content,
		"run_python_file": run_python_file,
		"write_file": write_file
	}

	if function_call_part.name in functions_dict:
		function_to_call = functions_dict[function_call_part.name]
		result = function_to_call(**{**function_call_part.args, "working_directory": "./calculator"})

		return types.Content(
			role="tool",
			parts=[
				types.Part.from_function_response(
					name=function_call_part.name,
					response={"result": result},
				)
			],
		)
	else:
		return types.Content(
			role="tool",
			parts=[
				types.Part.from_function_response(
					name=function_call_part.name,
					response={"error": f"Unknown function: {function_call_part.name}"},
				)
			],
		)
