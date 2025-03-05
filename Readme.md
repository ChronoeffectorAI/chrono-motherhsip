# ChronoEffector Framework

A flexible framework for creating, managing, and orchestrating AI agents with scheduling capabilities and dynamic agent loading.

## Overview

The ChronoEffector Framework provides a robust infrastructure for deploying, verifying, and orchestrating AI agents. It includes:

- A base agent class that can be extended for custom functionality
- An orchestrator for managing agent execution and scheduling
- A verification system to ensure agent quality and reliability
- Sample agent implementations for common use cases
- Dynamic agent loading capabilities via FastAPI

## Components

### Core Framework (`chronoeffector_framework.py`)

Contains the base classes and core functionality:

- `ChronoAgent`: Base class for all agents
- `AgentRegistry`: Registry to manage and verify agents
- `SolanaSmartContract`: For agent staking and validation
- `Validator`: For validating agent outputs

### Orchestrator (`orchestrator.py`)

Manages agent execution and scheduling:

- Schedules agent executions
- Processes execution queue
- Maintains execution history
- Provides API endpoints for agent management
- Supports dynamic agent loading from modules or file paths

### Sample Agents (`sample_agents.py`)

Example agent implementations:

- `WeatherAgent`: Fetches weather data
- `DataProcessingAgent`: Processes data according to rules
- `NotificationAgent`: Sends notifications through various channels

### Agent Verifier (`agent_verifier.py`)

Tool for verifying agent functionality:

- Runs test cases against agents
- Measures performance metrics
- Generates verification reports

## Usage

### Creating a Custom Agent

```python
from chronoeffector_framework import ChronoAgent

class MyCustomAgent(ChronoAgent):
    def __init__(self, agent_id, custom_config=None):
        super().__init__(agent_id, capabilities=["my_capability"])
        self.custom_config = custom_config or {}
        
    def execute(self, context):
        # Implement your agent's logic here
        result = {"status": "success", "data": "Custom agent result"}
        return result
        
    def validate(self):
        basic_valid = super().validate()
        # Add custom validation logic
        return basic_valid and "required_setting" in self.custom_config
```

### Registering and Using Agents Programmatically

```python
from chronoeffector_framework import AgentRegistry
from orchestrator import ChronoOrchestrator

# Create an orchestrator
orchestrator = ChronoOrchestrator()

# Create and register an agent
my_agent = MyCustomAgent("agent_1", {"required_setting": "value"})
orchestrator.register_agent(my_agent)

# Execute the agent
result = orchestrator.execute_agent("agent_1", {"param": "value"})
print(result)

# Schedule execution for later
from datetime import datetime, timedelta
future_time = datetime.now() + timedelta(minutes=5)
orchestrator.schedule_execution("agent_1", {"param": "value"}, future_time)

# Start the orchestrator to process scheduled executions
orchestrator.start()
```

### Deploying Agents via API

The framework supports multiple ways to dynamically deploy agents:

#### 1. Using Predefined Agent Types

```bash
curl -X POST "http://localhost:8000/deploy_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "weather_1",
    "agent_type": "weather",
    "config": {
      "api_key": "your_api_key_here"
    }
  }'
```

#### 2. Loading from a Module

```bash
curl -X POST "http://localhost:8000/deploy_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "custom_1",
    "agent_module": "my_custom_agent",
    "agent_class": "MyCustomAgent",
    "config": {
      "api_key": "your_api_key_here",
      "custom_param": "value"
    }
  }'
```

#### 3. Loading from a File Path

```bash
curl -X POST "http://localhost:8000/deploy_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "custom_2",
    "agent_path": "/path/to/my_custom_agent.py",
    "config": {
      "api_key": "your_api_key_here"
    }
  }'
```

### Executing Tasks via API

```bash
curl -X POST "http://localhost:8000/execute_task" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "weather_1",
    "context": {
      "location": "New York"
    }
  }'
```

### Scheduling Tasks via API

```bash
curl -X POST "http://localhost:8000/schedule_task" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "weather_1",
    "context": {
      "location": "London"
    },
    "execution_time": "2023-08-15T14:30:00"
  }'
```

### Managing Agents via API

```bash
# List all agents
curl -X GET "http://localhost:8000/list_agents"

# Get agent details
curl -X GET "http://localhost:8000/agent_info/weather_1"

# Unload an agent
curl -X POST "http://localhost:8000/unload_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "weather_1"
  }'
```

### Verifying Agents

```python
from agent_verifier import AgentVerifier

verifier = AgentVerifier()
verifier.register_agent(my_agent)

# Define test contexts
test_contexts = [
    {"test_id": "test1", "param": "value1"},
    {"test_id": "test2", "param": "value2"}
]

# Run verification
results = verifier.verify_agent("agent_1", test_contexts)
print(f"Verification passed: {results['passed']}")

# Generate a report
report = verifier.generate_report("agent_1")
print(report)
```

## API Endpoints

The framework provides REST API endpoints for agent management:

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|-------------|
| `/deploy_agent` | POST | Deploy a new agent | `agent_id`, `agent_type`/`agent_module`/`agent_path`, `config` |
| `/execute_task` | POST | Execute a task with a specified agent | `agent_id`, `context` |
| `/schedule_task` | POST | Schedule a task for future execution | `agent_id`, `context`, `execution_time` |
| `/unload_agent` | POST | Unload an agent | `agent_id` |
| `/list_agents` | GET | List all active agents | Query param: `capability` (optional) |
| `/agent_info/{agent_id}` | GET | Get detailed information about an agent | Path param: `agent_id` |

## Dynamic Agent Loading

The framework supports three methods for loading agents:

1. **Predefined Types**: Using built-in agent types like "weather", "data_processor", etc.
2. **Module Loading**: Loading agent classes from Python modules using `importlib`
3. **File Path Loading**: Loading agent classes from Python files at specific paths

This flexibility allows you to:
- Deploy pre-built agents quickly
- Create custom agents in separate modules
- Load agents from external sources or user-provided code

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Requests

## Installation

```bash
pip install -r requirements.txt
```

## Running the Example

```bash
# Start the orchestrator API server
python orchestrator.py

# Run the example usage script
python example_usage.py
```

## Security Considerations

When using dynamic agent loading, especially from external sources, consider these security practices:

1. **Input Validation**: Validate all inputs to prevent injection attacks
2. **Sandboxing**: Consider running untrusted code in a sandbox environment
3. **Access Control**: Implement proper authentication and authorization
4. **Resource Limits**: Apply CPU, memory, and time limits to agent execution

## License

MIT




