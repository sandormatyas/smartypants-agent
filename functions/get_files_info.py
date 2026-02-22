import os
from google.genai import types


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    try:
        working_directory_abs = os.path.abspath(working_directory)
        target_directory = os.path.normpath(
            os.path.join(working_directory_abs, directory)
        )

        is_valid_target = (
            os.path.commonpath([working_directory_abs, target_directory])
            == working_directory_abs
        )
        if not is_valid_target:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_directory):
            return f'Error: "{directory}" is not a directory'

        directory_contents = []
        for file in os.listdir(target_directory):
            file_size = os.path.getsize(os.path.join(target_directory, file))
            is_directory = os.path.isdir(os.path.join(target_directory, file))
            directory_contents.append(
                f"- {file}: file_size={file_size} bytes, is_dir={is_directory}"
            )

        return "\n".join(directory_contents)
    except Exception as e:
        return f'Error: Unable to access "{directory}": {str(e)}'


get_files_info("../", "../calculator")
