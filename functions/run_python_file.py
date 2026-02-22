import os
import subprocess
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file relative to the working directory, with optional arguments, and returns the output or any errors",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of string arguments to pass to the Python file when executing",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)


def run_python_file(working_directory, file_path, args=None):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        is_valid_target = (
            os.path.commonpath([working_directory_abs, target_file])
            == working_directory_abs
        )
        if not is_valid_target:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        absolute_file_path = os.path.abspath(target_file)
        command = ["python", absolute_file_path]
        if args:
            command.extend(args)

        process_result = subprocess.run(
            command,
            cwd=working_directory_abs,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if process_result.returncode != 0:
            return f"Process exited with code {process_result.returncode}"

        if process_result.stderr is None or process_result.stdout is None:
            return "No output produced"

        return f"STDOUT: {process_result.stdout}\nSTDERR: {process_result.stderr}"

    except Exception as e:
        return f"Error: executing Python file: {e}"
