from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Base class for all specialized agents in the Beregne platform.
    All agents must inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        self.agent_name = "base"
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """
        Determines if this agent can handle the given query.
        
        Args:
            query: The user's input query
            
        Returns:
            bool: True if the agent can handle this query, False otherwise
        """
        pass
    
    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes the query and returns a response.
        
        Args:
            query: The user's input query
            context: Optional context from previous interactions
            
        Returns:
            Dict containing response and metadata
        """
        pass
    
    def get_agent_name(self) -> str:
        """Returns the name of this agent"""
        return self.agent_name
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Returns information about what this agent can do"""
        return {
            "name": self.agent_name,
            "description": "Base agent class",
            "keywords": []
        }