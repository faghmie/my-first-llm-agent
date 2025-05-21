import yaml
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AgentConfig:
    name: str
    version: str
    description: str

@dataclass
class ModelConfig:
    name: str
    provider: str
    api_key: str
    parameters: Dict[str, float]

@dataclass
class AgentSystemPrompt:
    role: str
    system_context: str
    instructions: str
    constraints: str
    
@dataclass
class AgentPrompts:
    greeting: str
    error_response: str
    system: str
    
@dataclass
class AIConfig:
    agent: AgentConfig
    model: ModelConfig
    tools: List[Dict]
    # prompts: Dict[str, str]
    prompts: AgentPrompts
    metadata: Dict[str, str]

def load_agent_config(file_path: str) -> AIConfig:
    # Load the YAML file
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    return AIConfig(
        agent=AgentConfig(**config_data['agent']),
        model=ModelConfig(**config_data['model']),
        tools=config_data['tools'],
        prompts=config_data['prompts'],
        metadata=config_data['metadata']
    )

# Usage example
if __name__ == "__main__":
    config = load_agent_config('agents/delivery_fortnightly_report.yml')
    
    print(f"Agent Name: {config.agent.name}")
    print(f"Model: {config.model.name} ({config.model.provider})")
    print(f"Temperature: {config.model.parameters['temperature']}")
    print(f"System Prompt: {config.prompts['system']}")