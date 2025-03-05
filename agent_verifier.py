"""
Verification tool for ChronoEffector agents.
"""

import time
import json
import logging
from chronoeffector_framework import ChronoAgent, AgentRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AgentVerifier")

class AgentVerifier:
    """Tool for verifying ChronoEffector agents."""
    
    def __init__(self):
        """Initialize the verifier."""
        self.registry = AgentRegistry()
        self.verification_results = {}
        
    def register_agent(self, agent):
        """Register an agent for verification.
        
        Args:
            agent (ChronoAgent): Agent to verify
            
        Returns:
            bool: True if registration successful
        """
        return self.registry.register(agent)
        
    def verify_agent(self, agent_id, test_contexts=None):
        """Verify an agent's functionality.
        
        Args:
            agent_id (str): ID of the agent to verify
            test_contexts (list, optional): List of test contexts to run
            
        Returns:
            dict: Verification results
        """
        logger.info(f"Starting verification for agent {agent_id}")
        
        # Get basic verification from registry
        basic_verification = self.registry.verify_agent(agent_id)
        if not basic_verification["passed"]:
            logger.error(f"Agent {agent_id} failed basic verification")
            return basic_verification
            
        # Get the agent
        agent = self.registry.get_agent(agent_id)
        
        # Prepare results
        results = {
            "basic_verification": basic_verification,
            "execution_tests": {},
            "performance": {},
            "passed": basic_verification["passed"]
        }
        
        # If no test contexts provided, create a simple one
        if not test_contexts:
            test_contexts = [{"test_id": "default_test"}]
            
        # Run execution tests
        for context in test_contexts:
            test_id = context.get("test_id", f"test_{len(results['execution_tests'])}")
            
            try:
                # Measure execution time
                start_time = time.time()
                execution_result = agent.execute(context)
                execution_time = time.time() - start_time
                
                # Store results
                results["execution_tests"][test_id] = {
                    "context": context,
                    "result": execution_result,
                    "success": True,
                    "execution_time": execution_time
                }
                
                # Store performance data
                if "performance" not in results:
                    results["performance"] = {}
                    
                results["performance"][test_id] = {
                    "execution_time": execution_time
                }
                
            except Exception as e:
                logger.error(f"Agent {agent_id} execution failed for test {test_id}: {str(e)}")
                results["execution_tests"][test_id] = {
                    "context": context,
                    "error": str(e),
                    "success": False
                }
                results["passed"] = False
                
        # Store verification results
        self.verification_results[agent_id] = results
        
        # Log summary
        success_count = sum(1 for test in results["execution_tests"].values() if test["success"])
        total_tests = len(results["execution_tests"])
        logger.info(f"Agent {agent_id} verification complete: {success_count}/{total_tests} tests passed")
        
        return results
        
    def generate_report(self, agent_id=None):
        """Generate a verification report.
        
        Args:
            agent_id (str, optional): ID of the agent to report on
            
        Returns:
            str: JSON report
        """
        if agent_id:
            if agent_id not in self.verification_results:
                return json.dumps({"error": f"No verification results for agent {agent_id}"})
            return json.dumps(self.verification_results[agent_id], indent=2)
        else:
            # Generate summary report for all agents
            summary = {}
            for agent_id, results in self.verification_results.items():
                summary[agent_id] = {
                    "passed": results["passed"],
                    "test_count": len(results["execution_tests"]),
                    "success_count": sum(1 for test in results["execution_tests"].values() if test["success"])
                }
            return json.dumps(summary, indent=2) 