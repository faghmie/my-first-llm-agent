import json
import re
from datetime import datetime
from ollama import chat, ChatResponse
import threading

from agent import AgentToolbox
from agent import agent_config
from agent.timer_window import TimerWindow

class Agent():        
    def __init__(self):
        self.toolbox = AgentToolbox()
        self.messages = []
        self.stream_chunks = []

        self._done_event = threading.Event()
        self._result = None
        self._thread = None

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

        # with TimerWindow() as timer:
        #     timer.run_in_background(self.query_llm)
        # print(f'\n\n{timer.elapsed_time} elapsed\n\n')
        # return timer.result

        return self.query_llm()

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
                self.stream_chunks.append(content_part)
                # print(content_part, end='', flush=True)  # Stream to console
                full_response.append(content_part)
            
            # Check for tool invocation in the chunk (modify based on your model's output)
            if 'tool_calls' in chunk.get('message', {}):
                tools_to_invoke = chunk['message']['tool_calls']

        # print("\n")

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

    def _run_task(self, agent_config_file: str, user_input:str):
        """Internal thread runner"""
        try:
            self._done_event.clear()
            self._result = self.run(agent_config_file, user_input)
        finally:
            self._done_event.set()
    
    def run_async(self, agent_config_file: str, user_input:str):
        """Non-blocking version - returns immediately"""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Already running an async operation")
        
        self._thread = threading.Thread(
            target=self._run_task,
            args=(agent_config_file, user_input),
        )

        self._thread.start()

    def run_sync(self, agent_config_file: str, user_input:str):
        """Blocking version - waits for completion"""
        self.run_async(agent_config_file, user_input)
        self._thread.join()

    def is_done(self):
        """Check if task is completed"""
        return self._done_event.is_set()

    def get_result(self):
        """Get task result (raises error if not complete)"""
        if not self.is_done():
            return None
            # raise RuntimeError("Task not completed yet")

        return self._result
    
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
