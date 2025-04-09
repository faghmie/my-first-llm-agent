# Import all the necessary libraries
from dotenv import load_dotenv
import os

import ollama
from langchain_ollama import OllamaLLM, ChatOllama
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

# Load the environment variables from the .env file
load_dotenv()

questionToAsk = 'What is the answer to 1+1'

llm = ChatOllama(
    model=os.getenv("DEEPSEEK_MODEL"),
    temperature=0,
    base_url=os.getenv("DEEPSEEK_LOCAL_URL"),
    streaming=True,
)

def test_chat_ollama():
    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]
    ai_msg = llm.invoke(messages)

    print(ai_msg.content)

def simple_agent():

    # Add chat history to Agenst as short term memory
    chat_history = []

    # Add tools to the Agent to extent capabilities
    tools = []

    # Define the chat prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful personal AI assistant named TARS. You have a geeky, clever, sarcastic, and edgy sense of humor."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Define the agent
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"]
        }
        | prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    user_task = questionToAsk
    output = agent_executor.invoke({
        "input": user_task,
        "chat_history": chat_history
    })

    print(output["output"])


# llm = OllamaLLM(model=os.getenv("DEEPSEEK_MODEL"))
# response = llm.invoke(questionToAsk)
# print(response)

def test_ollama_directly():    
    messages = [
        {
            "role": "user",
            "content": questionToAsk
        }
    ]

    response = ollama.chat(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages
    )

    ollamaResponse = response["message"]["content"]

    print(ollamaResponse)


simple_agent()
