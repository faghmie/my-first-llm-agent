
# Does some sys.path manipulation so we can run examples in-place.
# noinspection PyUnresolvedReferences
import _example_config

from agent import Agent

# query for a summary report
#   highlight risks in the online order system

agent = Agent()
print(
    agent.run(
        agent_config_file="agent_scripts/requirements_risk_analysis.yml",
        user_input="loyalty_api_requirements.md"
    )
)