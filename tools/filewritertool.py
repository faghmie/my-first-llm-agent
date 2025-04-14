from tools.tool import Tool



class FileWriterTool(Tool):


    def name(self):

        return "Write To Disk"



    def description(self):

        return ("""
                **Description**:
                    This tool is used to write a text file to disk
                    - User should provide a name for the file
                    - if no name is provided, a default name will be used

                **Input Rules**:
                    - Type: Array[string, string]
                    - Number of Arguments: 2
                    - Max Length: 2
                    - Min Length: 2
                    - Example: ["my_file", "this is the content of the file"]
                    - arguments must be passed in the format: [filename, file_content]
                    - filename: this is the first argument and is the name of the file to be created
                    - file_content: this is the second argument and is the content to be written to the file
                    - **Example**: ["my_file", "this is the content of the file"]
                    - **Important**: The arguments must be passed as a list
                    - List must have **two elements ONLY**: 
                        - first element is the filename
                        - second element is the file content
                    - end of tool input rules

                """)


    def use(self, *args, **kwargs):

        print(args)

        file = args[0]


        if not file or len(file) < 2:

            return "Error: Please provide a filename and requirements to write to the file."
        

        filename = file[0]


        with open("prds/{filename}.txt", "w") as f:

            f.write(file[1] if args else "")


        return f"Requirements written to 'prds/requirements.txt'."