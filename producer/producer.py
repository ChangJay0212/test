"""
Producer implementation for simulating student requests
"""
import time
import uuid
import threading
from typing import Dict, Any, Optional
from core.kafka_client import kafka_client
from core.registry import agent_registry
from core.dynamic_assign import dynamic_assigner
from core.logger import logger
import config.settings as settings


class StudentProducer:
    """
    Producer that simulates student requests to the teaching system
    """
    
    def __init__(self, producer_uuid: str = None):
        self.producer_uuid = producer_uuid or str(uuid.uuid4())
        self.pending_requests: Dict[str, Dict] = {}
        self.result_consumer = None
        self.is_listening = False
        self.listener_thread = None
        
        logger.info(f"Student producer initialized: {self.producer_uuid}")
    
    def start_result_listener(self):
        """Start listening for results from agents"""
        if self.is_listening:
            logger.warning("Result listener already running")
            return
        
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_for_results, daemon=True)
        self.listener_thread.start()
        logger.info("Result listener started")
    
    def stop_result_listener(self):
        """Stop listening for results"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=5)
        if self.result_consumer:
            self.result_consumer.close()
        logger.info("Result listener stopped")
    
    def send_question(self, message: str, agent_type: str = None) -> str:
        """
        Send a question to the teaching system
        
        Args:
            message: Student question
            agent_type: Specific agent type to use (optional)
            
        Returns:
            Request ID for tracking the response
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Determine target topic
            if agent_type:
                # Find specific agent topic
                target_topic = self._get_topic_for_agent_type(agent_type)
                if not target_topic:
                    logger.error(f"Unknown agent type: {agent_type}")
                    return None
            else:
                # Use dynamic assignment
                target_topic = dynamic_assigner.assign_agent(message)
                if not target_topic:
                    logger.error("Failed to assign agent for message")
                    return None
            
            # Prepare message
            kafka_message = {
                "message": message,
                "producer_uuid": self.producer_uuid,
                "request_id": request_id,
                "timestamp": time.time()
            }
            
            # Send message to appropriate topic
            kafka_client.send_message(target_topic, kafka_message)
            
            # Track pending request
            self.pending_requests[request_id] = {
                "message": message,
                "target_topic": target_topic,
                "timestamp": time.time(),
                "status": "pending"
            }
            
            logger.info(f"Question sent to {target_topic}: {message[:50]}...")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to send question: {e}")
            return None
    
    def _get_topic_for_agent_type(self, agent_type: str) -> Optional[str]:
        """
        Get topic for specific agent type
        
        Args:
            agent_type: Agent type
            
        Returns:
            Topic name or None if not found
        """
        for agent_info in agent_registry.list_agents():
            if agent_info.agent_type == agent_type:
                return agent_info.topic
        return None
    
    def _listen_for_results(self):
        """Listen for results from agents"""
        try:
            # Create consumer for result topic
            self.result_consumer = kafka_client.get_consumer(
                [settings.TOPIC_RESULT],
                group_id=f"producer_{self.producer_uuid}"
            )
            
            logger.info("Listening for results...")
            
            while self.is_listening:
                try:
                    # Poll for messages
                    message_pack = self.result_consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, messages in message_pack.items():
                        for message in messages:
                            self._handle_result_message(message.value)
                            
                except Exception as e:
                    if self.is_listening:  # Only log if we're still supposed to be running
                        logger.error(f"Error polling for results: {e}")
                    
        except Exception as e:
            logger.error(f"Error in result listener: {e}")
        finally:
            if self.result_consumer:
                self.result_consumer.close()
    
    def _handle_result_message(self, message: Dict[str, Any]):
        """
        Handle result message from agents
        
        Args:
            message: Result message from agent
        """
        try:
            producer_uuid = message.get('producer_uuid')
            
            # Check if this message is for us
            if producer_uuid != self.producer_uuid:
                return
            
            request_id = message.get('request_id')
            if request_id in self.pending_requests:
                # Update request status
                self.pending_requests[request_id]['status'] = 'completed'
                self.pending_requests[request_id]['response'] = message
                
                # Log result
                agent_type = message.get('agent_type', 'unknown')
                success = message.get('success', False)
                
                if success:
                    response_text = message.get('response', '')
                    logger.info(f"Received response from {agent_type}: {response_text[:100]}...")
                    print(f"\n=== Response from {agent_type} ===")
                    print(f"Question: {self.pending_requests[request_id]['message']}")
                    print(f"Answer: {response_text}")
                    print("=" * 50)
                else:
                    error = message.get('error', 'Unknown error')
                    logger.error(f"Error response from {agent_type}: {error}")
                    print(f"\n=== Error from {agent_type} ===")
                    print(f"Question: {self.pending_requests[request_id]['message']}")
                    print(f"Error: {error}")
                    print("=" * 50)
            
        except Exception as e:
            logger.error(f"Error handling result message: {e}")
    
    def get_pending_requests(self) -> Dict[str, Dict]:
        """
        Get list of pending requests
        
        Returns:
            Dictionary of pending requests
        """
        return self.pending_requests.copy()
    
    def send_sample_questions(self):
        """Send some sample questions for testing"""
        sample_questions = [
            "What is the difference between 'affect' and 'effect'?",
            "Can you explain the theme of Shakespeare's Romeo and Juliet?",
            "What is the meaning of the Chinese idiom '畫蛇添足'?",
            "Help me analyze this poem: 'Two roads diverged in a yellow wood'",
            "What are the key elements of classical Chinese poetry?",
            "How do I improve my English writing skills?"
        ]
        
        print("Sending sample questions...")
        for question in sample_questions:
            request_id = self.send_question(question)
            if request_id:
                print(f"Sent: {question}")
                time.sleep(2)  # Wait between questions
            else:
                print(f"Failed to send: {question}")


# Demo function for testing
def run_producer_demo():
    """Run a demo of the producer functionality"""
    producer = StudentProducer()
    
    try:
        # Start listening for results
        producer.start_result_listener()
        
        # Wait a moment for listener to start
        time.sleep(1)
        
        # Send sample questions
        producer.send_sample_questions()
        
        # Wait for responses
        print("\nWaiting for responses...")
        time.sleep(30)
        
        # Show pending requests
        pending = producer.get_pending_requests()
        print(f"\nPending requests: {len(pending)}")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        producer.stop_result_listener()


if __name__ == "__main__":
    run_producer_demo()
