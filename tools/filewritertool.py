from tools.tool import Tool


class FileWriterTool(Tool):

    """
        This tool is used to write a text file to disk
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def use(self, filename: str, content: str) -> str:
        """
        This function takes a JSON object as an argument and writes its content to a file
        specified in the JSON object. 
        If no filename or content is provided, this function will return an error message
        
        Args:
            filename (str): Name/path of the file to save
            content (str): Text content to write to the file
        
        Returns:
            str: A string message indicating whether the file was written successfully
        """
        
        try:
            with open(f"prds/{filename}", "w") as f:
                f.write(content)

        except Exception:
            return "Error : JSON object not found in the LLM response."


        return f"Requirements written to 'prds/{filename}'."
