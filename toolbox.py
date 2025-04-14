from tools.tool import Tool


from tools.filewritertool import FileWriterTool

from tools.prdtemplatestool import PRDTemplateGeneratorTool


class Toolbox:

    def __init__(self):

        self.tools = []

        # self.add_tool(PRDTemplateGeneratorTool())
        self.add_tool(FileWriterTool())


    def add_tool(self, tool):
        self.tools.append(tool)
    

    def get_tool_list(self):
        
        return "\n".join([f"""
            ### Tool: `{tool.name()}` \n 
            **Name**: {tool.name()} \n  
            {tool.description()}\n""" for tool in self.tools]
        )
    def get_tool_names(self):
    
        return "\n".join(
            [f"- {tool.name()}" for tool in self.tools]
        )
    

    