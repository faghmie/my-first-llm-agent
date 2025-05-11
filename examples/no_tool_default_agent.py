
# Does some sys.path manipulation so we can run examples in-place.
# noinspection PyUnresolvedReferences
import _example_config

import time
from agent import Agent

stream_index = 0

agent = Agent()
agent.run_async(agent_config_file="agent_scripts/_default_agent.yml", user_input="what is the current date")

def print_stream():
    global stream_index

    current_index = stream_index
    max_index = len(agent.stream_chunks)
    content = ""
    for i in range(current_index, max_index):
        stream_index = i + 1
        content += agent.stream_chunks[i]

    if len(content) > 0:
        print(f'{content}', end='', flush=True)
    
while not agent.is_done():
    print_stream()
    time.sleep(0.1)  # import time

print_stream()