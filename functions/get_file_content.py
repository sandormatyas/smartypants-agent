import os
from config import MAX_READ_CHARS
from google.genai import types


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the content of a specified file relative to the working directory, with a maximum character limit to prevent excessive output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file to read from, relative to the working directory (default is the working directory itself)",
            )
        },
    ),
)


def get_file_content(working_directory, file_path):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        is_valid_target = (
            os.path.commonpath([working_directory_abs, target_file])
            == working_directory_abs
        )
        if not is_valid_target:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read(MAX_READ_CHARS)

            # After reading the first MAX_READ_CHARS...
            if f.read(1):
                content += (
                    f'[...File "{file_path}" truncated at {MAX_READ_CHARS} characters]'
                )

        return content

    except Exception as e:
        return f'Error: Unable to read file "{file_path}": {str(e)}'
