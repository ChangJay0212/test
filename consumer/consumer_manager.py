"""
Consumer manager for managing agent consumers
"""
import time
import threading
from typing import Dict
from core.kafka_client import kafka_client
from core.registry import agent_registry
from core.logger import logger
from agents.english_teacher import EnglishTeacherAgent
from agents.chinese_teacher import ChineseTeacherAgent
import config.settings as settings


class AgentConsumer:
    """
    Consumer wrapper for individual agents
    """
    
    def __init__(self, agent, topic: str):
        self.agent = agent
        self.topic = topic
        self.consumer = None
        self.is_running = False
        self.consumer_thread = None
        self.message_count = 0
        
    def start_consuming(self):
        """Start consuming messages for this agent"""
        if self.is_running:
            logger.warning(f"Consumer for {self.agent.agent_type} already running")
            return
        
        self.is_running = True
        self.consumer_thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.consumer_thread.start()
        logger.info(f"Started consumer for {self.agent.agent_type} on topic {self.topic}")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.is_running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
        if self.consumer:
            self.consumer.close()
        logger.info(f"Stopped consumer for {self.agent.agent_type}")
    
    def _consume_loop(self):
        """Main consumption loop"""
        try:
            # Create Kafka consumer
            self.consumer = kafka_client.get_consumer(
                [self.topic],
                group_id=f"agent_{self.agent.agent_uuid}"
            )
            
            logger.info(f"Consumer for {self.agent.agent_type} listening on {self.topic}")
            
            while self.is_running:
                try:
                    # Poll for messages
                    message_pack = self.consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, messages in message_pack.items():
                        for message in messages:
                            self._process_message(message.value)
                            
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Error in consumer loop for {self.agent.agent_type}: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Fatal error in consumer for {self.agent.agent_type}: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def _process_message(self, message: Dict):
        """
        Process individual message
        
        Args:
            message: Message from Kafka
        """
        try:
            self.message_count += 1
            logger.info(f"{self.agent.agent_type} processing message #{self.message_count}")
            
            # Process message with agent
            result = self.agent.process_message(message)
            
            # Add request_id to result if present in original message
            if 'request_id' in message:
                result['request_id'] = message['request_id']
            
            # Send result back to result topic
            kafka_client.send_message(settings.TOPIC_RESULT, result)
            
            logger.info(f"{self.agent.agent_type} completed processing message #{self.message_count}")
            
        except Exception as e:
            logger.error(f"Error processing message in {self.agent.agent_type}: {e}")
            
            # Send error response
            error_result = {
                "success": False,
                "error": f"Message processing failed: {str(e)}",
                "agent_type": self.agent.agent_type,
                "agent_uuid": self.agent.agent_uuid,
                "producer_uuid": message.get('producer_uuid', ''),
                "request_id": message.get('request_id', '')
            }
            
            try:
                kafka_client.send_message(settings.TOPIC_RESULT, error_result)
            except Exception as send_error:
                logger.error(f"Failed to send error response: {send_error}")


class ConsumerManager:
    """
    Manager for all agent consumers
    """
    
    def __init__(self):
        self.consumers: Dict[str, AgentConsumer] = {}
        self.is_running = False
        
    def initialize_agents(self):
        """Initialize and register all agent consumers"""
        try:
            # Create agent instances
            agents = [
                EnglishTeacherAgent(),
                ChineseTeacherAgent()
            ]
            
            # Create consumers for each agent
            for agent in agents:
                # Get topic for this agent from registry
                agent_info = agent_registry.get_agent_by_uuid(agent.agent_uuid)
                if agent_info:
                    consumer = AgentConsumer(agent, agent_info.topic)
                    self.consumers[agent.agent_uuid] = consumer
                    logger.info(f"Registered consumer for {agent.agent_type}")
                else:
                    logger.error(f"Agent {agent.agent_uuid} not found in registry")
            
            logger.info(f"Initialized {len(self.consumers)} agent consumers")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def start_all_consumers(self):
        """Start all agent consumers"""
        if self.is_running:
            logger.warning("Consumers already running")
            return
        
        try:
            # Ensure topics exist
            topics = [settings.TOPIC_ENGLISH_TEACHER, settings.TOPIC_CHINESE_TEACHER, settings.TOPIC_RESULT]
            kafka_client.create_topics(topics)
            
            # Start all consumers
            for consumer in self.consumers.values():
                consumer.start_consuming()
            
            self.is_running = True
            logger.info("All agent consumers started")
            
        except Exception as e:
            logger.error(f"Failed to start consumers: {e}")
            raise
    
    def stop_all_consumers(self):
        """Stop all agent consumers"""
        self.is_running = False
        
        for consumer in self.consumers.values():
            consumer.stop_consuming()
        
        logger.info("All agent consumers stopped")
    
    def get_consumer_status(self) -> Dict[str, Dict]:
        """
        Get status of all consumers
        
        Returns:
            Dictionary containing consumer status information
        """
        status = {}
        for agent_uuid, consumer in self.consumers.items():
            status[agent_uuid] = {
                "agent_type": consumer.agent.agent_type,
                "topic": consumer.topic,
                "is_running": consumer.is_running,
                "message_count": consumer.message_count
            }
        return status
    
    def run_forever(self):
        """
        Run consumer manager indefinitely
        Useful for production deployment
        """
        logger.info("Consumer manager running indefinitely...")
        try:
            while self.is_running:
                time.sleep(10)  # Check every 10 seconds
                
                # Health check - ensure all consumers are still running
                for agent_uuid, consumer in self.consumers.items():
                    if not consumer.is_running:
                        logger.warning(f"Consumer {agent_uuid} stopped unexpectedly, restarting...")
                        consumer.start_consuming()
                        
        except KeyboardInterrupt:
            logger.info("Consumer manager interrupted by user")
        finally:
            self.stop_all_consumers()


# Global consumer manager instance
consumer_manager = ConsumerManager()


def run_consumers():
    """Main function to run all consumers"""
    try:
        # Initialize agents
        consumer_manager.initialize_agents()
        
        # Start all consumers
        consumer_manager.start_all_consumers()
        
        # Run forever
        consumer_manager.run_forever()
        
    except Exception as e:
        logger.error(f"Error running consumers: {e}")
        raise
    finally:
        consumer_manager.stop_all_consumers()


if __name__ == "__main__":
    run_consumers()
