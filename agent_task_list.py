from agent_base import AgentBase
from tools.filewritertool import FileWriterTool

class AgentTaskList(AgentBase):
    def name(self):
        return "Task List Agent"
    
    def description(self):
        return f"""
        An agent that helps generate a task list for a new software product that needs to be built.
    """

    def run(self):        
        self.set_prompt(
            "prompts/prompt_task_list.md"
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

    agent.run()