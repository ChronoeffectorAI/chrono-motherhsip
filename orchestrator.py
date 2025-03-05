from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import uvicorn
import time
import logging
import importlib
import inspect
import sys
import os
from datetime import datetime
from chronoeffector_framework import AgentRegistry, ChronoAgent

# FastAPI app instance
app = FastAPI(title="Chronoeffector AI Orchestrator")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ChronoOrchestrator")

class ChronoOrchestrator:
    """Main orchestrator for the ChronoEffector framework.
    
    Manages agent execution, scheduling, and coordination.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.registry = AgentRegistry()
        self.execution_queue = []
        self.execution_history = []
        self.running = False
        logger.info("ChronoOrchestrator initialized")
    
    def register_agent(self, agent):
        """Register an agent with the orchestrator.
        
        Args:
            agent (ChronoAgent): Agent to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            result = self.registry.register(agent)
            logger.info(f"Agent {agent.agent_id} registered successfully")
            return result
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to register agent: {str(e)}")
            raise
    
    def schedule_execution(self, agent_id, context=None, execution_time=None):
        """Schedule an agent for execution.
        
        Args:
            agent_id (str): ID of the agent to execute
            context (dict, optional): Execution context
            execution_time (datetime, optional): When to execute the agent
        
        Returns:
            str: Execution ID
        """
        if agent_id not in self.registry.agents:
            logger.error(f"Cannot schedule unknown agent: {agent_id}")
            raise ValueError(f"Agent {agent_id} not registered")
            
        execution_id = f"exec_{int(time.time())}_{agent_id}"
        
        execution_entry = {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "context": context or {},
            "scheduled_time": execution_time or datetime.now(),
            "status": "scheduled"
        }
        
        self.execution_queue.append(execution_entry)
        logger.info(f"Scheduled execution {execution_id} for agent {agent_id}")
        return execution_id
    
    def execute_agent(self, agent_id, context=None):
        """Execute an agent immediately.
        
        Args:
            agent_id (str): ID of the agent to execute
            context (dict, optional): Execution context
            
        Returns:
            dict: Execution results
        """
        try:
            agent = self.registry.get_agent(agent_id)
            
            # Verify agent before execution
            verification = self.registry.verify_agent(agent_id)
            if not verification["passed"]:
                logger.error(f"Agent {agent_id} failed verification: {verification}")
                raise RuntimeError(f"Agent {agent_id} failed verification")
            
            execution_context = context or {}
            
            logger.info(f"Executing agent {agent_id}")
            start_time = time.time()
            
            try:
                result = agent.execute(execution_context)
                status = "completed"
            except Exception as e:
                logger.error(f"Agent {agent_id} execution failed: {str(e)}")
                result = {"error": str(e)}
                status = "failed"
                
            execution_time = time.time() - start_time
            
            execution_record = {
                "agent_id": agent_id,
                "context": execution_context,
                "result": result,
                "status": status,
                "execution_time": execution_time,
                "timestamp": datetime.now()
            }
            
            self.execution_history.append(execution_record)
            agent.last_execution = execution_record
            
            logger.info(f"Agent {agent_id} execution {status} in {execution_time:.2f}s")
            return result
            
        except KeyError:
            logger.error(f"Agent {agent_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error executing agent {agent_id}: {str(e)}")
            raise
    
    def process_queue(self):
        """Process all scheduled executions that are due."""
        current_time = datetime.now()
        pending_executions = []
        
        for execution in self.execution_queue:
            if execution["scheduled_time"] <= current_time:
                try:
                    agent_id = execution["agent_id"]
                    context = execution["context"]
                    
                    execution["status"] = "running"
                    result = self.execute_agent(agent_id, context)
                    
                    execution["status"] = "completed"
                    execution["result"] = result
                    execution["completed_time"] = datetime.now()
                    
                    self.execution_history.append(execution)
                except Exception as e:
                    execution["status"] = "failed"
                    execution["error"] = str(e)
                    self.execution_history.append(execution)
            else:
                pending_executions.append(execution)
        
        self.execution_queue = pending_executions
    
    def start(self):
        """Start the orchestrator's main loop."""
        self.running = True
        logger.info("ChronoOrchestrator started")
        
        try:
            while self.running:
                self.process_queue()
                time.sleep(1)  # Check queue every second
        except KeyboardInterrupt:
            logger.info("ChronoOrchestrator stopped by user")
        except Exception as e:
            logger.error(f"ChronoOrchestrator error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the orchestrator's main loop."""
        self.running = False
        logger.info("ChronoOrchestrator stopped")

# Initialize the orchestrator
orchestrator = ChronoOrchestrator()

# Pydantic models for request validation
class DeployAgentRequest(BaseModel):
    agent_id: str
    agent_type: Optional[str] = None
    agent_module: Optional[str] = None
    agent_class: Optional[str] = None
    agent_path: Optional[str] = None
    config: Dict[str, Any] = {}

class ExecuteTaskRequest(BaseModel):
    agent_id: str
    context: Dict[str, Any] = {}

class ScheduleTaskRequest(BaseModel):
    agent_id: str
    context: Dict[str, Any] = {}
    execution_time: Optional[datetime] = None

class UnloadAgentRequest(BaseModel):
    agent_id: str

# Helper function to dynamically load agent classes
def load_agent_class(module_name, class_name=None):
    """
    Dynamically load an agent class from a module.
    
    Args:
        module_name (str): Name of the module to import
        class_name (str, optional): Name of the class to load. If None, will find first ChronoAgent subclass.
        
    Returns:
        type: The agent class
    """
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # If class name is provided, get that specific class
        if class_name:
            if not hasattr(module, class_name):
                raise ValueError(f"Class {class_name} not found in module {module_name}")
            
            agent_class = getattr(module, class_name)
            if not issubclass(agent_class, ChronoAgent):
                raise ValueError(f"Class {class_name} is not a ChronoAgent subclass")
            
            return agent_class
        
        # Otherwise, find the first ChronoAgent subclass
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ChronoAgent) and obj != ChronoAgent:
                return obj
        
        raise ValueError(f"No ChronoAgent subclass found in module {module_name}")
    
    except ImportError as e:
        raise ImportError(f"Failed to import module {module_name}: {str(e)}")

# API Endpoints
@app.post("/deploy_agent")
async def deploy_agent(request: DeployAgentRequest):
    """Dynamically deploy an AI agent."""
    agent_id = request.agent_id
    config = request.config
    
    try:
        # Method 1: Use predefined agent types
        if request.agent_type:
            if request.agent_type == "weather":
                # Try to import from sample_agents
                try:
                    from sample_agents import WeatherAgent
                    agent_class = WeatherAgent
                except ImportError:
                    raise HTTPException(status_code=400, detail="WeatherAgent not found. Make sure sample_agents.py is available.")
            
            elif request.agent_type == "data_processor":
                try:
                    from sample_agents import DataProcessingAgent
                    agent_class = DataProcessingAgent
                except ImportError:
                    raise HTTPException(status_code=400, detail="DataProcessingAgent not found. Make sure sample_agents.py is available.")
            
            elif request.agent_type == "notification":
                try:
                    from sample_agents import NotificationAgent
                    agent_class = NotificationAgent
                except ImportError:
                    raise HTTPException(status_code=400, detail="NotificationAgent not found. Make sure sample_agents.py is available.")
            
            else:
                raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        # Method 2: Load from a specified module and class
        elif request.agent_module:
            try:
                agent_class = load_agent_class(request.agent_module, request.agent_class)
            except (ImportError, ValueError) as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Method 3: Load from a file path
        elif request.agent_path:
            try:
                # Add the directory to sys.path if it's not the current directory
                agent_dir = os.path.dirname(request.agent_path)
                if agent_dir and agent_dir not in sys.path:
                    sys.path.append(agent_dir)
                
                # Get the module name (filename without .py)
                module_name = os.path.basename(request.agent_path)
                if module_name.endswith('.py'):
                    module_name = module_name[:-3]
                
                # Load the agent class
                agent_class = load_agent_class(module_name, request.agent_class)
            except (ImportError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Failed to load agent from path {request.agent_path}: {str(e)}")
        
        else:
            raise HTTPException(status_code=400, detail="Must specify either agent_type, agent_module, or agent_path")
        
        # Create and register the agent
        agent = agent_class(agent_id, **config)
        orchestrator.register_agent(agent)
        
        return {
            "message": f"Agent {agent_id} deployed successfully",
            "agent_class": agent_class.__name__,
            "capabilities": agent.capabilities
        }
    
    except Exception as e:
        logger.error(f"Error deploying agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy agent: {str(e)}")

@app.post("/execute_task")
async def execute_task(request: ExecuteTaskRequest):
    """Execute a task with a specified agent."""
    agent_id = request.agent_id
    context = request.context
    
    try:
        result = orchestrator.execute_agent(agent_id, context)
        return {
            "agent_id": agent_id,
            "result": result
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.post("/schedule_task")
async def schedule_task(request: ScheduleTaskRequest):
    """Schedule a task for future execution."""
    agent_id = request.agent_id
    context = request.context
    execution_time = request.execution_time
    
    try:
        execution_id = orchestrator.schedule_execution(agent_id, context, execution_time)
        return {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "scheduled_time": execution_time or datetime.now()
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

@app.post("/unload_agent")
async def unload_agent(request: UnloadAgentRequest):
    """Unload an agent from the system."""
    agent_id = request.agent_id
    
    try:
        if agent_id not in orchestrator.registry.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Remove from registry
        del orchestrator.registry.agents[agent_id]
        if agent_id in orchestrator.registry.verification_results:
            del orchestrator.registry.verification_results[agent_id]
        
        return {"message": f"Agent {agent_id} unloaded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unload agent: {str(e)}")

@app.get("/list_agents")
async def list_agents(capability: Optional[str] = None):
    """List all active agents, optionally filtered by capability."""
    try:
        agents = orchestrator.registry.list_agents(capability)
        
        # Get more details about each agent
        agent_details = {}
        for agent_id in agents:
            agent = orchestrator.registry.agents[agent_id]
            agent_details[agent_id] = {
                "class": agent.__class__.__name__,
                "capabilities": agent.capabilities,
                "status": agent.status,
                "last_execution": agent.last_execution["timestamp"] if agent.last_execution else None
            }
        
        return {"agents": agent_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")

@app.get("/agent_info/{agent_id}")
async def agent_info(agent_id: str):
    """Get detailed information about a specific agent."""
    try:
        if agent_id not in orchestrator.registry.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = orchestrator.registry.agents[agent_id]
        verification = orchestrator.registry.verification_results.get(agent_id, {})
        
        return {
            "agent_id": agent_id,
            "class": agent.__class__.__name__,
            "module": agent.__class__.__module__,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "verification": verification,
            "last_execution": agent.last_execution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent info: {str(e)}")

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)