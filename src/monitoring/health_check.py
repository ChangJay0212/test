"""
Health check module for monitoring Kafka and agent status
"""

import threading
import time
from typing import Dict

import src.config.settings as settings
from src.agents.registry import agent_registry
from src.messaging.kafka_client import kafka_client
from src.utils.logger import logger


class HealthChecker:
    """
    HealthChecker class for monitoring system components.
    """

    def __init__(self):
        self.is_running = False
        self.health_thread = None
        self.kafka_status = "unknown"
        self.agent_statuses: Dict[str, str] = {}
        self.startup_time = time.time()
        self.startup_grace_period = 60  # 60 seconds grace period after startup

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
        """Enhanced Kafka cluster health check"""
        try:
            admin_client = kafka_client.admin_client
            if not admin_client:
                self.kafka_status = "disconnected"
                logger.warning("Kafka admin client not available")
                return

            # Get cluster information (no timeout parameter)
            # Cluster metadata: {'throttle_time_ms': 0, 'brokers': [{'node_id': 1, 'host': 'kafka', 'port': 29092, 'rack': None}], 'cluster_id': 'peOO_oKxTkC2_2ymUNKyXw', 'controller_id': 1}
            cluster_metadata = admin_client.describe_cluster()

            # Extract broker and controller info
            broker_count = 0
            controller = None

            if cluster_metadata and isinstance(cluster_metadata, dict):
                # cluster_metadata is a dict, not an object
                brokers = cluster_metadata.get("brokers", [])
                broker_count = len(brokers) if brokers else 0
                controller = cluster_metadata.get("controller_id", None)

            # Get topics list
            # topics_metadata: ['result', 'chinese_teacher', 'english_teacher', '__consumer_offsets']
            topics_metadata = admin_client.list_topics()
            topic_list = []

            # topics_metadata is directly a list, not an object with .topics attribute
            if topics_metadata and isinstance(topics_metadata, list):
                topic_list = topics_metadata
            elif topics_metadata and hasattr(topics_metadata, "topics"):
                # Fallback in case the API returns an object
                topic_list = (
                    list(topics_metadata.topics.keys())
                    if topics_metadata.topics
                    else []
                )

            # Health assessment logic
            min_broker_count = getattr(settings, "MIN_BROKER_COUNT", 1)

            # Check if we're in startup grace period
            startup_grace_active = (
                time.time() - self.startup_time
            ) < self.startup_grace_period

            # Debug information
            logger.info(
                f"Health check debug: broker_count={broker_count}, controller={controller}, min_broker_count={min_broker_count}"
            )
            logger.info(f"Topic list: {topic_list}")
            logger.info(f"Has __consumer_offsets: {'__consumer_offsets' in topic_list}")
            logger.info(f"Startup grace period active: {startup_grace_active}")

            if broker_count >= min_broker_count and controller is not None:
                # Check for system topics or any topics
                if "__consumer_offsets" in topic_list or len(topic_list) > 0:
                    self.kafka_status = "healthy"
                    logger.info(
                        f"Kafka healthy: {broker_count} brokers, {len(topic_list)} topics, controller={controller}"
                    )
                elif startup_grace_active:
                    # During startup, don't require topics to exist yet
                    self.kafka_status = "healthy"
                    logger.info(
                        f"Kafka healthy (startup grace): {broker_count} brokers, controller={controller}, topics will be created soon"
                    )
                else:
                    self.kafka_status = "degraded"
                    logger.warning(
                        "Kafka connected but no topics found (possible permission issue)"
                    )
            elif broker_count > 0:
                self.kafka_status = "degraded"
                logger.warning(
                    f"Kafka partially available: {broker_count} broker(s) active, controller={controller}, min_required={min_broker_count}"
                )
            else:
                self.kafka_status = "unhealthy"
                logger.error("Kafka cluster unreachable or no brokers available")

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
                logger.warning(
                    f"Agent health check failed for {agent_info.agent_uuid}: {e}"
                )
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
            "timestamp": time.time(),
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
            status for status in self.agent_statuses.values() if status == "active"
        ]

        return len(healthy_agents) > 0


# Global health checker instance
health_checker = HealthChecker()
