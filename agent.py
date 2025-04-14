import json
import re
import logging
import json

from toolbox import Toolbox

from dotenv import load_dotenv
import os

from langchain_ollama import OllamaLLM, ChatOllama

class Agent:
    def __init__(self):
        self.toolbox = Toolbox()
        self.memory = []
        self.max_memory = 10
        self.agent_prompt = None

    def load_prompt(self, prompt_path="prompt_analyst.md"):
        with open(prompt_path, "r") as f:
            self.agent_prompt = f.read()

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

                    # raise ValueError("No JSON object found in the LLM response.")
            # Parse the JSON string
            print(f"JSON string:\n {json_str}\n")
            json_dict = json.loads(json_str)
            if isinstance(json_dict, dict):
                return json_dict

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")

        print(f"LLM response was: {input_string}")

        raise ValueError("Invalid JSON response from LLM.")

    def clean_llm_response(self, input_string):
        # Remove the <think> and </think> tags from DeepSeek response
        cleaned = re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL).strip()
        return cleaned

    def process_input(self, user_input):
        short_term_memory = "\n".join(self.memory)

        self.memory.append(f"User: {user_input}")
        self.memory = self.memory[-self.max_memory:]

        prompt = self.agent_prompt.format(
            short_term_memory   = short_term_memory,
            available_tools     = self.toolbox.get_tool_list(),
            user_input          = user_input,
            tool_names          = self.toolbox.get_tool_names(),
        )

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        print(prompt)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

        response = self.query_llm(prompt)
        
        self.memory.append(f"Agent: {response}")

        response_dict = self.json_parser(response)

        # Handle the tool or response
        if response_dict["action"] == "respond_to_user":
            answer = response_dict["args"]
            self.memory.append(f"<answer> {answer}</answer>")
            return answer
            # return response_dict["args"]
        else:
            # Find and use the appropriate tool
            for tool in self.toolbox.tools:
                if tool.name().lower() == response_dict["action"].lower():
                    answer = tool.use(response_dict["args"])
                    self.memory.append(f"<answer> {answer}</answer>")
                    return answer

        return "I'm sorry, I couldn't process your request."

    def query_llm(self, prompt):
        llm = ChatOllama(
            model=os.getenv("DEEPSEEK_MODEL"),
            temperature=0.7,
            base_url=os.getenv("DEEPSEEK_LOCAL_URL"),
            streaming=True,
        )

        ai_msg = llm.invoke(prompt)
        print("<ai-message>")
        print(ai_msg.content)
        print("</ai-message>")
        
        return self.clean_llm_response(ai_msg.content)

    def run(self):
        
        load_dotenv()
        self.load_prompt()

        print("LLM Agent: Hello! How can I assist you today?")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "bye", "close"]:
                print("Agent: See you later!")
                break
            response = self.process_input(user_input)
            print(f"Agent: {response}")

# I have received a new request from the user to build a new dashboard for enterprise users to track API usage analytics
# Now save the requirements to a file

if __name__ == "__main__":
    agent = Agent()
    agent.run()