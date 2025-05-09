import json
import re
from datetime import datetime
from ollama import chat, ChatResponse

from agent import AgentToolbox
from agent import agent_config
from agent.timer_window import TimerWindow

class Agent():        
    def __init__(self):
        self.toolbox = AgentToolbox()
        self.messages = []

        print("AgentBase::__init__()")

    def clean_llm_response(self, input_string):
        # Remove the <think> and </think> tags from DeepSeek response
        cleaned = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL).strip()
        return cleaned

    def process_input(self, user_input):
        if len(self.messages) == 0:
            raise ValueError("Agent prompt not set. Please set a agent prompt first.")

        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        # print(self.messages[0]["content"])  # Print the agent prompt
        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

        self.messages.append({
                "role": "user",
                "content": user_input
            })

        with TimerWindow() as timer:
            timer.run_in_background(self.query_llm)
        # response = self.query_llm()
        print(f'\n\n{timer.elapsed_time} elapsed\n\n')

        return timer.result

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

    def run(self, agent_config_file: str = "agents/_default_agent.yml", user_input:str = None):
        
        self.AgentConfig = agent_config.load_agent_config(agent_config_file)

        self.messages = [{
            "role": "system", 
            "content": self.AgentConfig.prompts['system']
        },
        {
            "role": "tool", 
            "content": datetime.now().strftime("%Y-%m-%d"),
            "name": "current calendar date"
        }
        ]

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
