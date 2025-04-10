import requests
import json
import ast
import re

from tools.tool import Tool
from tools.timetool import TimeTool
from tools.calculatortool import CalculatorTool

from dotenv import load_dotenv
import os

import ollama
from langchain_ollama import OllamaLLM, ChatOllama

class Agent:
    def __init__(self):
        self.tools = []
        self.memory = []
        self.max_memory = 10
        self.agent_prompt = None

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def load_prompt(self, prompt_path="prompt.txt"):
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
                    raise ValueError("No JSON object found in the LLM response.")
            # Parse the JSON string
            json_dict = json.loads(json_str)
            if isinstance(json_dict, dict):
                return json_dict
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")

        print(f"LLM response was: {input_string}")

        raise ValueError("Invalid JSON response from LLM.")

    def process_input(self, user_input):
        context = "\n".join(self.memory)

        self.memory.append(f"User: {user_input}")
        self.memory = self.memory[-self.max_memory:]

        tool_descriptions = "\n".join(
            [f"- {tool.name()}: {tool.description()}" for tool in self.tools]
        )

        prompt = self.agent_prompt.format(
            context=context,
            tool_descriptions=tool_descriptions,
            user_input=user_input)

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(prompt)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

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
            for tool in self.tools:
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
        print(ai_msg.content)
        return ai_msg.content

        # gemini= LLM("vertexai/gemini-1.5-pro-latest", api_key= GOOGLE_API_KEY)
        # response=gemini.chat(prompt).choices[0].message.content.strip()
        # return response

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

if __name__ == "__main__":
    agent = Agent()
    agent.add_tool(TimeTool())
    agent.add_tool(CalculatorTool())
    agent.run()