from typing import Dict, Any, List, Optional
import logging
from .agents.base_agent import BaseAgent
from .agents.enhanced_renovation_agent import EnhancedRenovationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates all AI agents and routes queries to the appropriate specialist.
    This is the central hub that determines which agent should handle each query.
    """
    
    def __init__(self):
        self.agents: List[BaseAgent] = []
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        try:
            # Add enhanced renovation agent
            renovation_agent = EnhancedRenovationAgent()
            self.agents.append(renovation_agent)
            logger.info(f"Initialized agent: {renovation_agent.get_agent_name()}")
            
            # TODO: Add other agents (loan, energy, general) when they're created
            
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    async def route_query(self, query: str, context: Dict[str, Any] = None, partner_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Routes a query to the most appropriate agent.
        
        Args:
            query: The user's input query
            context: Optional context from previous interactions
            
        Returns:
            Dict containing the response and routing information
        """
        try:
            # Find the best agent for this query
            best_agent = self._find_best_agent(query, partner_config)
            
            if not best_agent:
                return {
                    "response": "Beklager, jeg forstod ikke spørsmålet ditt. Kan du prøve å omformulere det?",
                    "agent_used": "none",
                    "routing": {
                        "agent_used": "none",
                        "confidence": 0.0,
                        "reasoning": "Ingen agent kunne håndtere spørringen"
                    }
                }
            
            # Process the query with the selected agent
            result = await best_agent.process(query, context)
            
            # Add routing information
            result["routing"] = {
                "agent_used": best_agent.get_agent_name(),
                "confidence": 1.0,  # TODO: Implement confidence scoring
                "reasoning": f"Håndtert av {best_agent.get_agent_name()} agent"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            return {
                "response": f"Det oppstod en feil ved behandling av spørringen: {str(e)}",
                "agent_used": "error",
                "error": str(e)
            }
    
    def _find_best_agent(self, query: str, partner_config: Dict[str, Any] = None) -> Optional[BaseAgent]:
        """
        Finds the best agent to handle the given query.
        
        Args:
            query: The user's input query
            
        Returns:
            The best agent for this query, or None if no agent can handle it
        """
        # Filter agents based on partner configuration
        available_agents = self.agents
        if partner_config and "enabled_agents" in partner_config:
            enabled_agent_names = partner_config["enabled_agents"]
            available_agents = [
                agent for agent in self.agents 
                if agent.get_agent_name() in enabled_agent_names
            ]
        
        for agent in available_agents:
            try:
                if agent.can_handle(query):
                    return agent
            except Exception as e:
                logger.error(f"Error checking agent {agent.get_agent_name()}: {str(e)}")
                continue
        
        return None
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Returns information about all available agents"""
        return [agent.get_capabilities() for agent in self.agents]
    
    def get_agent_count(self) -> int:
        """Returns the number of active agents"""
        return len(self.agents)