"""
Example usage of the ChronoEffector framework with sample agents.
"""

import time
from datetime import datetime, timedelta
from chronoeffector_framework import ChronoAgent, AgentRegistry
from orchestrator import ChronoOrchestrator
from sample_agents import WeatherAgent, DataProcessingAgent, NotificationAgent
from agent_verifier import AgentVerifier

def main():
    print("ChronoEffector Framework Example")
    print("================================")
    
    # Create an orchestrator
    orchestrator = ChronoOrchestrator()
    
    # Create sample agents
    weather_agent = WeatherAgent("weather_1", api_key="sample_api_key_123")
    
    data_processing_agent = DataProcessingAgent(
        "data_processor_1", 
        processing_rules={
            "transform": {
                "name": "uppercase",
                "value": "double"
            },
            "filter": ["sensitive_data"]
        }
    )
    
    notification_agent = NotificationAgent(
        "notifier_1",
        notification_channels={
            "email": {"server": "smtp.example.com"},
            "sms": {"provider": "twilio"},
            "push": {"service": "firebase"}
        }
    )
    
    # Register agents with the orchestrator
    orchestrator.register_agent(weather_agent)
    orchestrator.register_agent(data_processing_agent)
    orchestrator.register_agent(notification_agent)
    
    print(f"Registered {len(orchestrator.registry.agents)} agents")
    
    # Verify agents
    verifier = AgentVerifier()
    verifier.register_agent(weather_agent)
    
    # Verify weather agent with test contexts
    weather_test_contexts = [
        {"test_id": "nyc_weather", "location": "New York"},
        {"test_id": "tokyo_weather", "location": "Tokyo"},
        {"test_id": "invalid_test", "wrong_param": "value"}  # This should fail
    ]
    
    weather_verification = verifier.verify_agent("weather_1", weather_test_contexts)
    print("\nWeather Agent Verification Results:")
    print(f"Passed: {weather_verification['passed']}")
    print(f"Tests run: {len(weather_verification['execution_tests'])}")
    print(f"Successful tests: {sum(1 for t in weather_verification['execution_tests'].values() if t['success'])}")
    
    # Schedule some executions
    print("\nScheduling agent executions...")
    
    # Execute weather agent now
    orchestrator.schedule_execution(
        "weather_1", 
        context={"location": "San Francisco"}
    )
    
    # Execute data processing agent in 5 seconds
    future_time = datetime.now() + timedelta(seconds=5)
    orchestrator.schedule_execution(
        "data_processor_1", 
        context={
            "data": {
                "name": "sample data",
                "value": 42,
                "sensitive_data": "should be filtered"
            }
        },
        execution_time=future_time
    )
    
    # Execute notification agent in 10 seconds
    future_time = datetime.now() + timedelta(seconds=10)
    orchestrator.schedule_execution(
        "notifier_1", 
        context={
            "channel": "email",
            "message": "Hello from ChronoEffector!"
        },
        execution_time=future_time
    )
    
    # Start the orchestrator (will process the queue)
    print("\nStarting orchestrator to process scheduled executions...")
    print("Press Ctrl+C to stop after 15 seconds")
    
    try:
        # Run for 15 seconds then stop
        orchestrator.start()
        time.sleep(15)
        orchestrator.stop()
    except KeyboardInterrupt:
        orchestrator.stop()
    
    # Print execution history
    print("\nExecution History:")
    for i, execution in enumerate(orchestrator.execution_history):
        print(f"{i+1}. Agent: {execution['agent_id']}, Status: {execution['status']}")
        if execution['status'] == 'completed':
            print(f"   Result: {execution['result']}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main() 