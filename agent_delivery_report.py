from agent_base import AgentBase
from tools.jira_tool import JiraTool

class AgentDeliveryReport(AgentBase):
    def name(self):
        return "Delivery Report Agent"
    
    def description(self):
        return f"""
        An agent that helps generate a delivery report for a new software product that needs to be built.
        """

    def json_array_to_markdown(self, json_data):
        # Extract headers from the keys of the first JSON object
        headers = list(json_data[0].keys())
        
        # Create the Markdown table header
        # markdown = ["| " + " | ".join(headers) + " |"]
        
        # Add the separator row
        # markdown.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        markdown = "--------------------\n";

        # Add each JSON object as a row
        for item in json_data:
            row = []
            for key in headers:
                value = str(item.get(key, "")).strip()
                markdown += f"""{key}: {value if value else 'N/A'}\n"""
                # Handle empty values and 'N/A' cases
                row.append(value if value else " ")
            # markdown.append("| " + " | ".join(row) + " |")
            markdown += "--------------------\n"

        return markdown
        # return "\n".join(markdown)
        
    def run(self):
        self.set_prompt(
            "prompts/prompt_delivery_report.md"
        )

        with open(f"""sample-tickets.md""", "r") as f:
            project_tickets = f.read()

        self.agent_prompt = self.safe_format(self.agent_prompt,
            project_tickets = project_tickets
        )

        # jira_tool = JiraTool()
        # project_tickets = jira_tool.use()

        # self.agent_prompt = self.safe_format(self.agent_prompt,
        #     project_tickets = self.json_array_to_markdown(project_tickets)
        # )

        print("LLM Agent: Hello! How can I assist you today?")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "bye", "close"]:
                print("Agent: See you later!")
                break
            response = self.process_input(user_input)
            print(f"Agent: {response}")

# describe what this project

# give me a summary of the completed work

# list the 5 tickets that is done and took the longest to reach completion and sort them in descending order


if __name__ == "__main__":
    agent = AgentDeliveryReport()
    # agent.add_tool(FileWriterTool())
    agent.run()