"""
Sample agent implementations for the ChronoEffector framework.
"""

import time
import random
import requests
from datetime import datetime
from chronoeffector_framework import ChronoAgent

class WeatherAgent(ChronoAgent):
    """Agent that fetches weather data for a location."""
    
    def __init__(self, agent_id, api_key):
        """Initialize the WeatherAgent.
        
        Args:
            agent_id (str): Unique identifier for this agent
            api_key (str): API key for weather service
        """
        super().__init__(agent_id, capabilities=["weather_lookup"])
        self.api_key = api_key
        
    def execute(self, context):
        """Fetch weather data for the specified location.
        
        Args:
            context (dict): Must contain 'location' key
            
        Returns:
            dict: Weather data
        """
        if 'location' not in context:
            raise ValueError("Context must include 'location'")
            
        location = context['location']
        
        # In a real implementation, this would call a weather API
        # For demo purposes, we'll simulate a response
        weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy"]
        
        # Simulate API call
        time.sleep(0.5)
        
        return {
            "location": location,
            "temperature": random.randint(0, 35),
            "condition": random.choice(weather_conditions),
            "humidity": random.randint(30, 90),
            "timestamp": datetime.now().isoformat()
        }
        
    def validate(self):
        """Validate the agent configuration.
        
        Returns:
            bool: True if valid
        """
        basic_valid = super().validate()
        return basic_valid and bool(self.api_key)


class DataProcessingAgent(ChronoAgent):
    """Agent that processes data according to specified rules."""
    
    def __init__(self, agent_id, processing_rules=None):
        """Initialize the DataProcessingAgent.
        
        Args:
            agent_id (str): Unique identifier for this agent
            processing_rules (dict, optional): Rules for data processing
        """
        super().__init__(agent_id, capabilities=["data_processing"])
        self.processing_rules = processing_rules or {}
        
    def execute(self, context):
        """Process data according to rules.
        
        Args:
            context (dict): Must contain 'data' key with data to process
            
        Returns:
            dict: Processed data
        """
        if 'data' not in context:
            raise ValueError("Context must include 'data'")
            
        data = context['data']
        processed_data = data.copy()  # Start with a copy
        
        # Apply processing rules
        if 'transform' in self.processing_rules:
            for field, transform in self.processing_rules['transform'].items():
                if field in processed_data:
                    if transform == 'uppercase' and isinstance(processed_data[field], str):
                        processed_data[field] = processed_data[field].upper()
                    elif transform == 'lowercase' and isinstance(processed_data[field], str):
                        processed_data[field] = processed_data[field].lower()
                    elif transform == 'double' and isinstance(processed_data[field], (int, float)):
                        processed_data[field] = processed_data[field] * 2
        
        if 'filter' in self.processing_rules:
            for field in list(processed_data.keys()):
                if field in self.processing_rules['filter']:
                    del processed_data[field]
        
        return {
            "original_data": data,
            "processed_data": processed_data,
            "rules_applied": list(self.processing_rules.keys()),
            "timestamp": datetime.now().isoformat()
        }


class NotificationAgent(ChronoAgent):
    """Agent that sends notifications through various channels."""
    
    def __init__(self, agent_id, notification_channels=None):
        """Initialize the NotificationAgent.
        
        Args:
            agent_id (str): Unique identifier for this agent
            notification_channels (dict, optional): Configuration for notification channels
        """
        super().__init__(agent_id, capabilities=["send_notification"])
        self.notification_channels = notification_channels or {}
        
    def execute(self, context):
        """Send a notification.
        
        Args:
            context (dict): Must contain 'message' and 'channel' keys
            
        Returns:
            dict: Notification result
        """
        if 'message' not in context:
            raise ValueError("Context must include 'message'")
            
        if 'channel' not in context:
            raise ValueError("Context must include 'channel'")
            
        channel = context['channel']
        message = context['message']
        
        if channel not in self.notification_channels:
            raise ValueError(f"Channel '{channel}' not configured")
            
        # In a real implementation, this would send actual notifications
        # For demo purposes, we'll simulate sending
        
        result = {
            "channel": channel,
            "message": message,
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
        
        # Simulate different channel behaviors
        if channel == "email":
            # Simulate email sending
            time.sleep(1.2)
        elif channel == "sms":
            # Simulate SMS sending
            time.sleep(0.8)
        elif channel == "push":
            # Simulate push notification
            time.sleep(0.5)
            
        return result
        
    def validate(self):
        """Validate the agent configuration.
        
        Returns:
            bool: True if valid
        """
        basic_valid = super().validate()
        return basic_valid and bool(self.notification_channels) 