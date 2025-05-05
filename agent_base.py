import json
import re
import os
from toolbox import Toolbox
from dotenv import load_dotenv
from ollama import chat, ChatResponse
from tools.tool import Tool
from string import Formatter
from busy_animation import BusyAnimation

class AgentBase(Tool):        
    def __init__(self):
        load_dotenv()

        self.toolbox = Toolbox()
        self.memory = []
        self.max_memory = 10
        self.agent_prompt = None
        self.messages = []

        print("AgentBase::__init__()")

    def add_tool(self, tool: Tool):
        self.toolbox.add_tool(tool)
        
    def set_prompt(self, prompt_path="prompt_analyst.md"):
        """
        Set the prompt that the agent will use to generate a response. This is typically
        a markdown file that describes what instructions the agent needs respond.

        Args:
            prompt_path (str): The path to the markdown file that defines the prompt
        """
        with open(prompt_path, "r") as f:
            self.agent_prompt = f.read()

        self.messages = [{"role": "system", "content": self.agent_prompt}]

    def json_parser(self, input_string):
        try:
            # Remove code block markers if present
            code_block_pattern = r"```json\s*(\{.*?\})\s*```"
            match = re.search(code_block_pattern, input_string, re.DOTALL)

            if match:
                json_str = match.group(1)
            else:
                # If no code block, try to match any JSON object in the string
                json_object_pattern = r"(\{.*?\})"

                match = re.search(json_object_pattern, input_string, re.DOTALL)

                if match:
                    json_str = match.group(1)
                else:
                    json_str = json.dumps({"action": "respond_to_user", "args": input_string})


            # Parse the JSON string
            json_dict = json.loads(json_str)

            if isinstance(json_dict, dict):
                return json_dict

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"\n\nLLM JSON was: {json_str}\n\n")


        print(f"LLM response was: {input_string}")

        raise ValueError("Invalid JSON response from LLM.")

    def safe_format(self, format_string, **kwargs):
        """
        Format a string while ignoring extra keyword arguments and leaving placeholders
        unchanged if their keys are not found in the kwargs.

        This is a wrapper around string.Formatter that behaves like string.format()
        but does not raise KeyError if a key is not found in the kwargs. It also
        filters out extra keyword arguments that are not used in the format string.

        For example, if the format string is "{foo} {bar}" and the kwargs are
        {"foo": "A", "bar": "B", "baz": "C"}, the result will be "A B" and the
        "baz" key will be ignored.

        :param format_string: The format string to format.
        :param **kwargs: The keyword arguments to format with.
        :return: The formatted string.
        """

        formatter = Formatter()
        result = []
        # Parse the format string to get all keys it requires
        required_keys = {field_name for _, field_name, _, _ in formatter.parse(format_string) if field_name is not None}
        # Filter kwargs to only include keys required by the format string (ignore extras)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in required_keys}
        
        # Process each part of the format string
        for literal_text, field_name, format_spec, conversion in formatter.parse(format_string):
            # Add literal text (non-placeholder parts)
            result.append(literal_text)
            if field_name is not None:
                # Substitute if the key exists in filtered_kwargs, else leave placeholder
                if field_name in filtered_kwargs:
                    obj = filtered_kwargs[field_name]
                    # Handle conversions (e.g., !r, !s)
                    if conversion:
                        obj = formatter.convert_field(obj, conversion)
                    # Apply format specifications (e.g., :03d)
                    formatted = formatter.format_field(obj, format_spec)
                    result.append(formatted)
                else:
                    # Rebuild the original placeholder (with conversion/formatting)
                    placeholder = "{" + field_name
                    if conversion:
                        placeholder += "!" + conversion
                    if format_spec:
                        placeholder += ":" + format_spec
                    placeholder += "}"
                    result.append(placeholder)
        return ''.join(result)

    def clean_llm_response(self, input_string):
        # Remove the <think> and </think> tags from DeepSeek response
        cleaned = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL).strip()
        return cleaned

    def process_response(self, response_string):
        """
        Override this function to process the response from the AI.
        
        Default Behavior:
            Process the response from the AI to determine if it is a tool usage
            or a direct response to the user.

        Args:
            response_string (str): The response from the AI.

        Returns:
            str: The answer to the user after processing the response.
        """
        response_dict = self.json_parser(response_string)

        # Handle the tool or response
        if response_dict["action"] == "respond_to_user":
            answer = response_dict["args"]
            self.memory.append(f"<answer> {answer}</answer>")
            return answer
        else:
            # Find and use the appropriate tool
            for tool in self.toolbox.tools:
                if tool.name().lower() == response_dict["action"].lower():
                    answer = tool.use(response_dict["args"])
                    self.memory.append(f"<answer> {answer}</answer>")
                    return answer

        return "I'm sorry, I couldn't process your request."

    def process_input(self, user_input):
        if len(self.messages) == 0:
            raise ValueError("Agent prompt not set. Please set a agent prompt first.")

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        print(self.agent_prompt)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

        self.messages.append({
                "role": "user",
                "content": user_input
            })

        # with BusyAnimation():
        response = self.query_llm()

        self.process_response(response)


    def query_llm(self):
        print("Querying LLM...")
        
        tools_schema = self.toolbox.get_registry()
        stream = chat(
            model = os.getenv("DEEPSEEK_MODEL"),
            messages = self.messages,
            tools = tools_schema,
            stream = True,
        )

        full_response = []
        tools_to_invoke = None

        for chunk in stream:
            # Stream the content incrementally
            content_part = chunk.get('message', {}).get('content', '')
            if content_part:
                print(content_part, end='', flush=True)  # Stream to console
                full_response.append(content_part)
            
            # Check for tool invocation in the chunk (modify based on your model's output)
            if 'tool_calls' in chunk.get('message', {}):
                tools_to_invoke = chunk['message']['tool_calls']


        return self.use_tool(full_response, tools_to_invoke)
        
    def use_tool(self, full_response, tools_to_invoke):
        # If no tools were found in chunks, check the full content
        if not tools_to_invoke:
            try:
                final_content = ''.join(full_response)
                parsed = json.loads(final_content)
                if 'tools' in parsed:
                    tools_to_invoke = parsed['tools']
            except json.JSONDecodeError:
                pass
        
        # Use the captured tool invocation data
        if tools_to_invoke:
            print(f"\n\nTools to invoke: {tools_to_invoke}")
            
            # Add logic to execute tools here
            for tool_call in tools_to_invoke:
                tool = tool_call["function"]
                tool_name = tool["name"]
                args = tool["arguments"]

                if (type(args) == str):
                    args = json.loads(tool["arguments"])
                
                if tool_name in self.toolbox.tools:
                    result = self.toolbox.tools[tool_name](**args)
                    
                    self.messages.append({"role": "tool", "content": str(result), "name": tool_name})    
                    
                    # Call the LLM with the tool result
                    return self.query_llm()
                else:
                    print(f"Tool {tool_name} not found!")

        
        ai_msg = ''.join(full_response)
        
        return self.clean_llm_response(ai_msg)

    def use(self, input_string):
        """
        Use the agent to process user input and generate a response.

        Args:
            input_string (str): The user's input.

        Returns:
            None
        """
        response = self.process_input(input_string)

        print(f"Agent: {response}")


class TestAgent(AgentBase):
    def run(self):    
        from tools.jira_epics import jira_epic_list_tool
        from tools.jira_tickets import jira_ticket_list_tool

        self.set_prompt(
            "prompts/prompt_delivery_lead.md"
        )

        print("Test-Agent: Hello! How can I assist you today?")
        
        self.add_tool(jira_epic_list_tool)
        self.add_tool(jira_ticket_list_tool)

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "bye", "close"]:
                print("Agent: See you later!")
                break

            self.use(user_input)



# I have received a new request from the user to build a new dashboard for enterprise users to track API usage analytics

# Now save the requirements to a file


if __name__ == "__main__":
    
    agent = TestAgent()
    agent.run()