from fastapi import FastAPI, HTTPException
from typing import Dict, Callable, Any
from pydantic import BaseModel
import uvicorn
import time

# FastAPI app instance
app = FastAPI(title="Chronoeffector AI Orchestrator")

# In-memory registry for active agents
class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, Callable] = {}  # agent_id -> task function
        self.metadata: Dict[str, Dict[str, Any]] = {}  # agent_id -> metadata (e.g., wallet_id, timestamp)

    def register_agent(self, agent_id: str, task_func: Callable, wallet_id: str) -> bool:
        """Register a new agent dynamically."""
        if agent_id in self.agents:
            return False
        self.agents[agent_id] = task_func
        self.metadata[agent_id] = {
            "wallet_id": wallet_id,
            "loaded_at": time.time()
        }
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unload an agent dynamically."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.metadata[agent_id]
            return True
        return False

    def get_agent(self, agent_id: str) -> Callable:
        """Retrieve an agent's task function."""
        return self.agents.get(agent_id)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all active agents with metadata."""
        return self.metadata

# Initialize the registry
registry = AgentRegistry()

# Pydantic models for request validation
class DeployAgentRequest(BaseModel):
    agent_id: str
    wallet_id: str
    # In a real system, you'd pass code or a reference to a task function.
    # For simplicity, we'll define a sample task inline in the endpoint.

class ExecuteTaskRequest(BaseModel):
    agent_id: str
    input_data: str

class UnloadAgentRequest(BaseModel):
    agent_id: str

# Sample agent task function (for demo purposes)
def sample_task(input_data: str) -> str:
    return f"Processed '{input_data}' by sample agent."

# API Endpoints
@app.post("/deploy_agent")
async def deploy_agent(request: DeployAgentRequest):
    """Dynamically deploy an AI agent."""
    agent_id = request.agent_id
    wallet_id = request.wallet_id
    
    # Simulate wallet-bound authentication (in reality, verify with Solana wallet signature)
    if not wallet_id.startswith("wallet_"):
        raise HTTPException(status_code=403, detail="Invalid wallet ID")

    # For this example, we use a hardcoded sample_task.
    # In a real system, you could load a Python function dynamically from a file or external source.
    success = registry.register_agent(agent_id, sample_task, wallet_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} already exists")
    
    return {
        "message": f"Agent {agent_id} deployed successfully",
        "wallet_id": wallet_id,
        "loaded_at": registry.metadata[agent_id]["loaded_at"]
    }

@app.post("/execute_task")
async def execute_task(request: ExecuteTaskRequest):
    """Execute a task with a specified agent."""
    agent_id = request.agent_id
    input_data = request.input_data
    
    agent_func = registry.get_agent(agent_id)
    if not agent_func:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    result = agent_func(input_data)
    return {
        "agent_id": agent_id,
        "result": result
    }

@app.post("/unload_agent")
async def unload_agent(request: UnloadAgentRequest):
    """Dynamically unload an AI agent."""
    agent_id = request.agent_id
    
    success = registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {"message": f"Agent {agent_id} unloaded successfully"}

@app.get("/list_agents")
async def list_agents():
    """List all active agents."""
    agents = registry.list_agents()
    if not agents:
        return {"message": "No agents currently active"}
    return {"active_agents": agents}

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)