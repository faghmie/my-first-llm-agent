import requests
import json
import ast
import re

from tool import Tool
from timetool import TimeTool
from calculatortool import CalculatorTool

from dotenv import load_dotenv
import os

import ollama
from langchain_ollama import OllamaLLM, ChatOllama

class Agent:
    def __init__(self):
        self.tools = []
        self.memory = []
        self.max_memory = 10

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

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

        self.memory.append(f"Old-User: {user_input}")
        self.memory = self.memory[-self.max_memory:]

        tool_descriptions = "\n".join(
            [f"- {tool.name()}: {tool.description()}" for tool in self.tools]
        )

        prompt = f"""You are an assistant that helps process user requests by determining the appropriate action and arguments based on the user's input.
                You will be provided with a context that you must use if needed to determine your response. Some available tools can be used to answer the user's request.
                You must only respond to the task provided in the final "User Input:" section.

                Context:

                This is the previous conversation history:
                {context}

                Available tools:
                {tool_descriptions}

                Instructions:
                - Decide whether to use a tool or respond directly to the user.
                - If you choose to use a tool, output a JSON object with "action" and "args" fields.
                - If you choose to respond directly, set "action": "respond_to_user" and provide your response in "args".
                - **Important**: Provide the response **only** as a valid JSON object. Do not include any additional text or formatting.
                - Ensure that the JSON is properly formatted without any syntax errors.

                Response Format:
                {{"action": "<action_name>", "args": "<arguments>"}}

                Example Responses:
                - Using a tool: {{"action": "Time Tool", "args": "Asia/Tokyo"}}
                - Responding directly: {{"action": "respond_to_user", "args": "I'm here to help!"}}

                The above is the end of the context. The following is the new user input:
                
                {user_input}

                """
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