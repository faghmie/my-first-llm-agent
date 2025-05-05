import inspect
import sys
import io
import re
import json
import importlib
import sys

class Toolbox:

    def __init__(self):

        self.tools = {}

        # self.add_tool(PRDTemplateGeneratorTool())
        # self.add_tool(FileWriterTool())


    def add_tool(self, tool):
        self.tools[tool.__name__] = tool
        # self.tools.append(tool)

    def docstring_to_tools_schema(self, obj):
        """Convert a function's docstring to Ollama tools schema format."""

        func = obj

        doc = inspect.getdoc(func)
        if not doc:
            raise ValueError("Function has no docstring")
        
        # Extract function description (first line before sections)
        description = re.split(r'\n\s*(Args|Returns|Raises|Examples):', doc)[0].strip()
        
        # Parse parameters
        params_section = re.search(r'Args:\s*(.*?)(?=\n\s*(Returns|Raises|Examples)|$)', doc, re.DOTALL)
        params = {}
        required = []
        
        if params_section:
            params_text = params_section.group(1).strip()
            for line in params_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Match parameter pattern: "name (type): description"
                match = re.match(r'(\w+)\s*(\(([^)]+)\))?:\s*(.*)', line)
                if match:
                    name = match.group(1)
                    param_type = match.group(3) or "string"  # Default to string
                    desc = match.group(4).strip()
                    
                    # Get JSON schema type from Python type
                    json_type = {
                        "str": "string",
                        "int": "integer",
                        "float": "number",
                        "bool": "boolean",
                        "list": "array",
                        "dict": "object"
                    }.get(param_type.lower(), "string")
                    
                    params[name] = {
                        "type": json_type,
                        "description": desc
                    }
                    
                    # Check if parameter is required (no default in function signature)
                    sig = inspect.signature(func)
                    param = sig.parameters.get(name)
                    if param and param.default == inspect.Parameter.empty:
                        required.append(name)
        
        # Build the tool schema
        return {
            "type": "function",
            "function": {
                "name": f"{obj.__name__}",
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required
                }
            }
        }
    
    def get_registry(self):
        reg = []
        for tool in self.tools:
            reg.append(self.docstring_to_tools_schema(self.tools[tool]))

        return reg

    def capture_help(self, cls):
        # Redirect stdout to a StringIO buffer
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        # Call help on the class
        help(cls)
        
        # Restore original stdout and get the captured content
        sys.stdout = old_stdout
        return buffer.getvalue()
    
    def get_tool_list(self):
        str_tools = ""
        for tool in self.tools:
            str_tools += f"""{self.capture_help(tool)}
                ---\n
            """
        
        return str_tools
        
    def get_tool_names(self):
    
        return "\n".join(
            [f"- {tool.name()}" for tool in self.tools]
        )

    def import_tools(self, tool_list: list = []):
        if not tool_list:
            return
        
        try:
            for tool in tool_list:
                # Extract configuration values
                module_name = tool['module']
                function_name = tool['function']
            
                # Import the specified module
                module = importlib.import_module(module_name)
                
                # Get the function from the module
                function = getattr(module, function_name)
            
                self.tools[function_name] = function
    
        except FileNotFoundError:
            raise Exception("Error: config.yaml file not found")
        except KeyError as e:
            raise Exception(f"Missing required key in config: {e}")
        except ImportError:
            raise Exception(f"Module '{module_name}' not found")
        except AttributeError:
            raise Exception(f"Function '{function_name}' not found in module '{module_name}'")
        except Exception as e:
            raise e

    