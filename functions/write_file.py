import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file relative to the working directory, creating any necessary directories, and returns a success message or any errors",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write to, relative to the working directory (e.g., 'subdir/file.txt')",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="String content to write to the specified file",
            ),
        },
    ),
)


def write_file(working_directory, file_path, content):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        is_valid_target = (
            os.path.commonpath([working_directory_abs, target_file])
            == working_directory_abs
        )
        if not is_valid_target:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except Exception as e:
        return f'Error: Unable to read file "{file_path}": {str(e)}'
