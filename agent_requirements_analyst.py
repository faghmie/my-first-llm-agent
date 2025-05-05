from agent_base import AgentBase
from tools.filewritertool import FileWriterTool

class AgentRequirementsAnalyst(AgentBase):
    def name(self):
        return "Requirements Analyst Agent"
    
    def description(self):
        return f"""
        An agent that helps generate requirements for a new dashboard for enterprise users to track API usage analytics.
    """

    def run(self):        
        self.set_prompt(
            "prompts/prompt_analyst.md"
        )

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
    agent = AgentRequirementsAnalyst()
    agent.add_tool(FileWriterTool())

    agent.run()