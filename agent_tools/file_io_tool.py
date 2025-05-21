
import os
from typing import List

def file_write_to_disk_tool(filename: str, content: str) -> str:
    """
    Write a text file to disk (in the `prd/` folder) with the given filename and content.

    Args:
        filename (str): The name of the file to write.
        content (str): The content to write to the file.

    Returns:
        str: A success message if the file was written, or an error message if not.
    """

    try:
        with open(f"prds/{filename}", "w") as f:
            f.write(content)

    except Exception as e:
        raise Exception(f"Error writing file:[{filename}] \n{str(e)}")


    return f'Requirements written to [prds/{filename}].'


def file_read_from_disk_tool(filename_with_path: str) -> str:
    """
    Read a file from disk and return its content as a string.

    Args:
        filename_with_path (str): The full path to the file to read.

    Returns:
        str: The content of the file if it was read successfully, or an error message if not.
    """
    response = ""
    try:
        with open(f"{filename_with_path}", "r") as f:
            response = f.read()

    except Exception as e:
        raise Exception(f"Error reading file:[{filename_with_path}] \n{str(e)}")

    return response

def file_list_from_disk_tool(base_path: str = None) -> List[str]:
    """
    Return a list of files from the given base_path.

    Args:
        base_path (str): The full path to the directory to list files from.

    Returns:
        List[str]: A list of filenames in the given base_path. If there is an error, an exception is raised.

    Raises:
        Exception: If the base_path is not provided, or if it does not exist, or if there is an error reading the directory.
    """
    
    if base_path is None or len(base_path) == 0:
        raise Exception("No base path provided")

    if not os.path.exists(base_path):
        raise Exception(f"Base path does not exist:[{base_path}]")

    response = ""
    try:
        files = os.listdir(base_path)
        # response = f"\n- ".join(files)

    except Exception as e:
        raise Exception(f"Error reading file:[{base_path}] \n{str(e)}")

    return files
    # return response


if __name__ == "__main__":
    print(file_list_from_disk_tool("sample_data/requirements"))
