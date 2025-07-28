"""
Health check module for monitoring Kafka and agent status
"""
import time
import threading
from typing import Dict
from core.logger import logger
from core.kafka_client import kafka_client
from core.registry import agent_registry
import config.settings as settings


class HealthChecker:
    """
    HealthChecker class for monitoring system components.
    """
    
    def __init__(self):
        self.is_running = False
        self.health_thread = None
        self.kafka_status = "unknown"
        self.agent_statuses: Dict[str, str] = {}
        
    def start_monitoring(self):
        """
        Start health monitoring in a separate thread.
        """
        if self.is_running:
            logger.warning("Health monitoring already running")
            return
            
        self.is_running = True
        self.health_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.health_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """
        Stop health monitoring.
        """
        self.is_running = False
        if self.health_thread:
            self.health_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """
        Main monitoring loop.

        Raises:
            Exception:
                An error occurred during monitoring.
        """
        while self.is_running:
            try:
                # Check Kafka health
                self._check_kafka_health()
                
                # Check agent health
                self._check_agent_health()
                
                # Sleep before next check
                time.sleep(settings.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(5)  # Short sleep on error
    
    def _check_kafka_health(self):
        """Check Kafka cluster health"""
        try:
            admin_client = kafka_client.admin_client
            if admin_client:
                # Try to list topics as a health check
                metadata = admin_client.describe_cluster(timeout_ms=settings.KAFKA_HEALTH_TIMEOUT * 1000)
                if metadata:
                    self.kafka_status = "healthy"
                else:
                    self.kafka_status = "unhealthy"
            else:
                self.kafka_status = "disconnected"
        except Exception as e:
            logger.warning(f"Kafka health check failed: {e}")
            self.kafka_status = "unhealthy"
    
    def _check_agent_health(self):
        """Check registered agent health"""
        for agent_info in agent_registry.list_agents():
            try:
                # For now, we assume agents are healthy if they're registered
                # In a real system, you might ping the agent or check last activity
                self.agent_statuses[agent_info.agent_uuid] = agent_info.status
            except Exception as e:
                logger.warning(f"Agent health check failed for {agent_info.agent_uuid}: {e}")
                self.agent_statuses[agent_info.agent_uuid] = "unhealthy"
    
    def get_system_health(self) -> Dict[str, any]:
        """
        Get overall system health status
        
        Returns:
            Dictionary containing health status of all components
        """
        return {
            "kafka": self.kafka_status,
            "agents": self.agent_statuses.copy(),
            "registered_agents": len(agent_registry.list_agents()),
            "timestamp": time.time()
        }
    
    def is_system_healthy(self) -> bool:
        """
        Check if the overall system is healthy
        
        Returns:
            True if system is healthy, False otherwise
        """
        # Check Kafka health
        if self.kafka_status != "healthy":
            return False
        
        # Check if at least one agent is healthy
        healthy_agents = [
            status for status in self.agent_statuses.values() 
            if status == "active"
        ]
        
        return len(healthy_agents) > 0


# Global health checker instance
health_checker = HealthChecker()
