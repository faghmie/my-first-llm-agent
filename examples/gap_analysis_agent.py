
# Does some sys.path manipulation so we can run examples in-place.
# noinspection PyUnresolvedReferences
import _example_config

from agent import Agent

agent = Agent()
agent.run(agent_config_file="agent_scripts/requirements_gap_analysis.yml")