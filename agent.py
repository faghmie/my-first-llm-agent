import json
import re
from toolbox import Toolbox
from ollama import chat, ChatResponse
from string import Formatter
from busy_animation import BusyAnimation

import agent_config

class Agent():        
    def __init__(self, agent_config_file: str ="agents/_default_agent.yml"):
        self.toolbox = Toolbox()
        self.memory = []
        self.max_memory = 10
        self.agent_prompt = None
        self.messages = []
        self.AgentConfig = agent_config.load_agent_config(agent_config_file)

        print("AgentBase::__init__()")

    def add_tool(self, tool):
        self.toolbox.add_tool(tool)
     
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

    def clean_llm_response(self, input_string):
        # Remove the <think> and </think> tags from DeepSeek response
        cleaned = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL).strip()
        return cleaned

    def process_input(self, user_input):
        if len(self.messages) == 0:
            raise ValueError("Agent prompt not set. Please set a agent prompt first.")

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        print(self.messages[0]["content"])  # Print the agent prompt
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

        self.messages.append({
                "role": "user",
                "content": user_input
            })

        # with BusyAnimation():
        response = self.query_llm()

        return response

    def query_llm(self):
        print("Querying LLM...")
        
        tools_schema = self.toolbox.get_registry()
        stream = chat(
            model = self.AgentConfig.model.name,
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

        print("\n")

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

    def run(self, user_input:str = None):
        self.messages = [{
            "role": "system", 
            "content": self.AgentConfig.prompts['system']
        }]

        print(f"Agent Name: {self.AgentConfig.agent.name}")
        print(f"Model: {self.AgentConfig.model.name} ({self.AgentConfig.model.provider})")

        print(self.AgentConfig.prompts['greeting'])
        
        # from tools.jira_epics import jira_epic_list_tool
        # from tools.jira_tickets import jira_ticket_list_tool
        
        # self.add_tool(jira_epic_list_tool)
        # self.add_tool(jira_ticket_list_tool)

        self.toolbox.import_tools(self.AgentConfig.tools)

        if user_input:
            return self.process_input(user_input)

        # If you get here you are in interactive mode
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "bye", "close"]:
                print("Agent: See you later!")
                break

            self.process_input(user_input)

# I have received a new request from the user to build a new dashboard for enterprise users to track API usage analytics

# Now save the requirements to a file

if __name__ == "__main__":   
    agent = Agent("agents/system_analyst_requirements.yml")
    agent.run()