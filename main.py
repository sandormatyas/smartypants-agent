import re
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function
import argparse

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

available_functions = [
    types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ],
    )
]

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

client = genai.Client(api_key=api_key)

completed_successfully = False
for _ in range(20):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, tools=available_functions
        ),
    )

    if response.usage_metadata is None:
        raise ValueError(
            "Usage metadata is missing from the response. The prompt might not have been processed correctly."
        )

    if response.candidates is not None:
        for c in response.candidates:
            messages.append(c.content)

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.function_calls is not None:
        fn_results = []
        for function_call in response.function_calls:
            content = call_function(function_call, verbose=args.verbose)

            if content.parts is None or len(content.parts) == 0:
                raise ValueError(
                    "Response parts are missing from the function call response. The function might not have been executed correctly."
                )

            if content.parts[0].function_response is None:
                raise ValueError(
                    "Function response is missing from the content parts. The function might not have been executed correctly."
                )

            if content.parts[0].function_response.response is None:
                raise ValueError(
                    "Function response content is missing from the function call response. The function might not have been executed correctly."
                )

            fn_results.append(content.parts[0])

            if args.verbose:
                print(f"-> {content.parts[0].function_response.response}")

        messages.append(types.Content(role="user", parts=fn_results))

    else:
        print(response.text)
        completed_successfully = True
        break

if not completed_successfully:
    print("Failed to complete the task within the maximum number of iterations.")
    exit(1)
