import json
import re
import shlex
import time

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

    def elapsed_time(self, seconds: int = None) -> str:
        if None is seconds:
            seconds = time.time() - self.start_time
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:05.2f}"
    
    def print_elapsed_time(self, msg: str = ""):
        print(f'\n\n{self.elapsed_time()} {msg}\n\n')
        
    def process_input(self, user_input):
        if len(self.messages) == 0:
            raise ValueError("Agent prompt not set. Please set a agent prompt first.")

        self.start_time = time.time()
        
        self.messages.append({
                "role": "user",
                "content": user_input
            })

        if self.interactive_mode:
            with TimerWindow() as timer:
                timer.run_in_background(self.query_llm)
                
            return timer.result

        response = self.query_llm()
        elapsed_time = self.elapsed_time()
        
        self.print_elapsed_time()
        
        return response

    def query_llm(self):
        self.print_elapsed_time("Query LLM...")
        streaming = False
        # tools_schema = self.toolbox.get_registry()

        stream = chat(
            model = self.AgentConfig.model.name,
            messages = self.messages,
            # tools = tools_schema,
            stream = streaming,
        )

        full_response = []
        tools_to_invoke = None

        if streaming:
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
        else:
            self.stream_chunks.append(stream.message.content)
            full_response.append(stream.message.content)

        return self.use_tool(full_response, tools_to_invoke)
        
    def use_tool(self, full_response, tools_to_invoke):
        
        self.print_elapsed_time("Use tools...")
        # If no tools were found in chunks, check the full content
        if not tools_to_invoke:
            try:
                final_content = self.clean_llm_response(''.join(full_response))
                
                parsed = json.loads(final_content.strip())
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
                    
                    self.messages.append({"role": "tool", "content": str(result), "name": f'{tool_name}'})
                    
                    # Call the LLM with the tool result
                    return self.query_llm()
                else:
                    raise ValueError(f"Tool {tool_name} not found!")

        
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
    
    def init_agent_system_messages(self):
        self.toolbox.import_tools(self.AgentConfig.tools)
        
        self.messages = [
            {
                "role": "system", 
                "content": self.AgentConfig.prompts['system']
            },
            {
                "role": "system", 
                "name": "real-time current calendar date",
                "content": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "role": "system",
                "content": f"""
                    ---
                    ## **Parsing User Input**
                        ### Natural Language Understanding (NLU)
                            - **Intent Recognition**  
                            Identify user goals (e.g., "book flight" vs. "cancel order").
                            - **Entity Extraction**  
                            Detect key details (dates, locations) using techniques like NER.
                            - **Context Awareness**  
                            Track conversation history (e.g., resolve "there" as "New York").
                            - **Syntax/Semantic Analysis**  
                            Parse sentence structure (e.g., "tomorrow" modifies "flight to Paris").
                            - **Ambiguity Resolution**  
                            Disambiguate terms (e.g., "play Coldplay" → song vs. artist).

                        ### Handling Variability
                            - **Adapt to dialects/typos**  
                            Normalize input (e.g., "pls send $$" → "Please send money").
                            - **Multi-Modal Support**  
                            Process text, voice, or images (e.g., photo of a bill for payment).

                        ### Compile Tool Response
                            - Understand the tool documentation.
                            - compile tool argument values
                            - Generate the tool response based on the tool response template
                    ---

                    ## **Tool Selection & Reasoning**
                        ### Tool Knowledge
                            - **Metadata Awareness**  
                            Understand tool purpose, parameters, and output formats.
                            - **Intent-Tool Mapping**  
                            Link goals to tools (e.g., "weather" → WeatherAPI).
                            - **Parameter Validation**  
                            Check for required inputs (e.g., "send email" needs a recipient).

                        ### Decision-Making
                            - **Prioritization**  
                            Rank tools by relevance (e.g., Uber > Lyft if user prefers).
                            - **Multi-Tool Orchestration**  
                            Chain tools for complex tasks (e.g., flight + hotel booking).
                            - **Fallback Strategies**  
                            Handle failures (e.g., "Google Maps down? Switch to Apple Maps").

                    ---
                    
                    ### Avilable Tools
                    {self.toolbox.get_registry()}

                    ---
                    
                    ### Tool Response Template
                        If you decide to use a tool then return the following JSON:
                        {{
                            "tools": [
                                {{
                                    "function":{{
                                        "name": "tool_name",
                                        "arguments": {{
                                            "paremeter_name": "parameter_value"
                                        }}
                                    }}
                                }}
                            ]
                        }}
                    
                    ---
                """
            },
        ]
        
    def run(self, agent_config_file: str = "agents/_default_agent.yml", user_input:str = None):
        self.interactive_mode = False
        self.AgentConfig = agent_config.load_agent_config(agent_config_file)

        self.init_agent_system_messages()

        print(f"Agent Name: {self.AgentConfig.agent.name}")
        print(f"Model: {self.AgentConfig.model.name} ({self.AgentConfig.model.provider})")


        if user_input:
            print(f"You: {user_input}")
            return self.process_input(user_input)

        print(self.AgentConfig.prompts['greeting'])
        
        self.interactive_mode = True
        # If you get here you are in interactive mode
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "bye", "close"]:
                print("Agent: See you later!")
                break

            print(self.process_input(user_input))
