
# Does some sys.path manipulation so we can run examples in-place.
# noinspection PyUnresolvedReferences
import _example_config

from agent import Agent

# query for a summary report
#   find gaps in the online order system

NEED MORE TESTING AGAINST SCRIPT

agent = Agent()
print(
    agent.run(
        agent_config_file="agent_scripts/requirements_gap_analysis.yml",
        user_input="find gaps in the online order system"
    )
)
