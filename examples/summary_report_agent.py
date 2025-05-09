
# Does some sys.path manipulation so we can run examples in-place.
# noinspection PyUnresolvedReferences
import _example_config

from agent import Agent

# query for a summary report
#   summarise the progress made over the last 7 days


agent = Agent()
agent.run(agent_config_file="agent_scripts/delivery_summary_report.yml")