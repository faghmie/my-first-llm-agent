
from tools.tool import Tool

class PRDTemplateGeneratorTool(Tool):
    def name(self):
        return "Requirement Template Generator"

    def description(self):
        return ("""
                **Description**:
                    Provides an a list of requirements to outline how a software solution should be built and the considerations. 
                    
                    When to Use:
                        - When defining solution for a new product, feature, or system.
                        - When stakeholders request a new product, feature, or system.
                        - When refining ambiguous requests into actionable specifications.
                        - When a software solution is requested

                **Input Rules**: 
                    - Type: string
                    - Max Length: 30
                    - Example: "Build a new API"
                    - Only pass the **one** string
                    - the string should not contain any special characters
                    - the string must not be json
                    - do not pass in lists "()" or arrays "[]"
                    - string should be short and concise
                    - string must be no more than 30 characters
                    - **Important**: The argument must be a simple string
                    - **only one string** must be passed into the tool
                    - **DO NOT** outline requirements
                    - end of tool input rules
                """)

    def use(self, *args, **kwargs):
        filename = None
        print(args[0])
        type = args[0].lower()
        print(type)
        if ("api" in type):
            filename = "api.prd"
        elif ("dashboard" in type):
            filename = "dashboard.prd"
        else:
            filename = "general.prd"
        
        file = open(f"prd_templates/{filename}", "r")

        return file.read()