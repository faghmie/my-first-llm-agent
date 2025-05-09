
import os

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

    except Exception:
        return "Error : JSON object not found in the LLM response."


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
        return f"Error reading file:[{filename_with_path}] \n{str(e)}"

    return response

def file_list_from_disk_tool(base_path: str = None) -> str:
    """
    Read a list of files from disk and return it as a string.

    Args:
        base_path (str): The full path to the directory to read.

    Returns:
        str: The list of files if it was read successfully, or an error message if not.
    """
    
    if base_path is None or len(base_path) == 0:
        return "Error: No base path provided."

    if not os.path.exists(base_path):
        return f"Error: Base path [{base_path}] does not exist."

    response = ""
    try:
        files = os.listdir(base_path)
        response = f"\n".join(files)

    except Exception as e:
        return f"Error reading file:[{base_path}] \n{str(e)}"

    return response


if __name__ == "__main__":
    print(file_list_from_disk_tool("sample_data"))
