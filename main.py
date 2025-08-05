import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import call_function

"""
main.py -- AI Coding Agent CLI

Uses Gemini's LLM with function declarations and a tool schema to allow structured file operations via natural language prompts.
Supported operations:
- Listing files and directories
- Reading file contents
- Executing Python files
- Writing or overwriting files

Usage:
	uv run main.py "<your prompt here>"

Environment variables:
	GEMINI_API_KEY: Your Gemini API key for authentication.
"""

def main():
	"""
	Entry point for the coding agent CLI.

	Loads configuration and function schemas for supported file actions. Reads a user prompt from the command line,
	sends it to the LLM, and prints the resulting function call plan or direct response.

	Expects the prompt as the first command-line argument.
	"""
	load_dotenv()
	api_key = os.environ.get("GEMINI_API_KEY")
	client = genai.Client(api_key=api_key)
	model_name = "gemini-1.5-flash"

	parser = argparse.ArgumentParser(description="AI Coding Agent CLI")
	parser.add_argument("prompt", help="The prompt to send to the AI")
	parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

	args = parser.parse_args()
	prompt = args.prompt
	verbose = args.verbose

	"""
	Initialize conversation with the user's initial prompt,
	formatted as a types.Content object
	"""
	conversation = [
		types.Content(role='user', parts=[types.Part(text=prompt)])
	]

	 # System prompt, schemas, available_functions, config:
	system_prompt = """
	You are a helpful AI coding agent that prioritized fulfilling questions/requests through tool usage, rather than text generation.
	
	IMPORTANT: When you need information, you must USE the available tools immediately. Do not explain what you plan to do - just do it.

	Whenever you receive a prompt, you must always start by calling get_files_info to explore all directories and files.
	After exploring files, immediately read potentially relevant files with get_file_content.
	Keep iterating with these tools before responding with any text.

	You should be strongly compelled to then investigate or explore the system when needing more context to answer the users questions/requests by performing the following operations:

	- Execute Python files with optional arguments with run_python
	- Write or overwrite files with write_file
	- Use available_functions to investigate or explore the system when needing more context to answer a question

	After gathering all relavent information in the system, provide a function call plan.

	Should any action be performed that results in writing a file or any code change, verify the results by executing the relavent code or re-reading specific file content if the change was purely textual.
	All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
	Whenever possible, your responses should summarize rather than providing raw file content.
	Only if you are unable to find the answer to the users questions/requests, offer relavent or applicable context or suggestions.
	"""
	schema_get_files_info = types.FunctionDeclaration(
		name="get_files_info",
		description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
		parameters=types.Schema(
			type=types.Type.OBJECT,
			properties={
				"directory": types.Schema(
					type=types.Type.STRING,
					description="The optional directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
				),
			},
		),
	)
	schema_get_file_content = types.FunctionDeclaration(
		name="get_file_content",
		description="Prints designated maximum amount of characters from files.",
		parameters=types.Schema(
			type=types.Type.OBJECT,
			properties={
				"file_path": types.Schema(
					type=types.Type.STRING,
					description="The file listed within the working directory to have its contents printed.",
				),
			},
		),
	)
	schema_run_python_file = types.FunctionDeclaration(
		name="run_python_file",
		description="Runs python programs & returns any STDOUT, STDERR & return codes.",
		parameters=types.Schema(
			type=types.Type.OBJECT,
			properties={
				"file_path": types.Schema(
					type=types.Type.STRING,
					description="The python source code file to run & return outputs. Return with appropriate description for non-python file or no output.",
				),
			},
		),
	)
	schema_write_file = types.FunctionDeclaration(
		name="write_file",
		description="Creates files if they don't exist & writes content into them.",
		parameters=types.Schema(
			type=types.Type.OBJECT,
			properties={
				"file_path": types.Schema(
					type=types.Type.STRING,
					description="The file to be written in the given path if within the working directory."),
				"content": types.Schema(
					type=types.Type.STRING,
					description="The content to be written in the given file."),
			},
		),
	)
	available_functions = types.Tool(
		function_declarations=[
			schema_get_files_info,
			schema_get_file_content,
			schema_run_python_file,
			schema_write_file
		]
	)
	config = types.GenerateContentConfig(
		tools=[available_functions],
		system_instruction=system_prompt
	)

	try:
		for _ in range(20):

			response = client.models.generate_content(
				model=model_name,
				contents=conversation,
				config=config
			)

			# Add model's candidates to conversation (if not broken)
			for candidate in response.candidates:
				conversation.append(candidate.content)

				# Handle function calls and add tool output to conversation (if not broken) (under model calls to avoid model invocation issues)
			if response.function_calls:
				for called_function in response.function_calls:
					print(f" - Calling function: {called_function.name}")
					function_call_result = call_function(called_function)
					if not function_call_result.parts[0].function_response.response:
						raise Exception("Function call result missing expected response structure") 
					if function_call_result.parts[0].function_response.response and verbose:
						print(f"-> {function_call_result.parts[0].function_response.response}")
					conversation.append(types.Content(role="tool", parts=function_call_result.parts))

			if response.text:
				print(f"Final response:\n{response.text}")
				break

		else:
			print("Agent stopped after 20 iterations to prevent an infinite loop.")
			print("The agent might still be thinking, or it may have reached a conclusion.")

	except Exception as e:
		print(f'Error: An unexpected error occured: {e}')


	

if __name__ == "__main__":
	main()
