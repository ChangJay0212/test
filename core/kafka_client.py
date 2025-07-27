"""
Kafka client wrapper for producer and consumer operations
"""
import json
from typing import Dict, Any, List
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from core.logger import logger
import config.settings as settings


class KafkaClient:
    """
    Kafka client wrapper for simplified producer/consumer operations
    """
    
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.producer = None
        self.admin_client = None
        self._initialize_admin_client()
    
    def _initialize_admin_client(self):
        """Initialize Kafka admin client"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='agentic_admin'
            )
            logger.info("Kafka admin client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka admin client: {e}")
    
    def get_producer(self) -> KafkaProducer:
        """
        Get or create Kafka producer
        
        Returns:
            KafkaProducer instance
        """
        if self.producer is None:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                logger.info("Kafka producer created successfully")
            except Exception as e:
                logger.error(f"Failed to create Kafka producer: {e}")
                raise
        return self.producer
    
    def get_consumer(self, topics: List[str], group_id: str = None) -> KafkaConsumer:
        """
        Create Kafka consumer for specified topics
        
        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            
        Returns:
            KafkaConsumer instance
        """
        if group_id is None:
            group_id = settings.KAFKA_CONSUMER_GROUP
            
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                consumer_timeout_ms=int(settings.CONSUMER_POLL_TIMEOUT * 1000)
            )
            logger.info(f"Kafka consumer created for topics: {topics}")
            return consumer
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            raise
    
    def create_topics(self, topics: List[str], num_partitions: int = 1, replication_factor: int = 1):
        """
        Create Kafka topics if they don't exist
        
        Args:
            topics: List of topic names to create
            num_partitions: Number of partitions per topic
            replication_factor: Replication factor
        """
        if not self.admin_client:
            logger.error("Admin client not available")
            return
            
        try:
            existing_topics = self.list_topics()
            topics_to_create = [
                NewTopic(
                    name=topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                )
                for topic in topics if topic not in existing_topics
            ]
            
            if topics_to_create:
                result = self.admin_client.create_topics(topics_to_create)
                for topic, future in result.items():
                    try:
                        future.result()
                        logger.info(f"Topic '{topic}' created successfully")
                    except Exception as e:
                        logger.warning(f"Failed to create topic '{topic}': {e}")
            else:
                logger.info("All topics already exist")
                
        except Exception as e:
            logger.error(f"Failed to create topics: {e}")
    
    def list_topics(self) -> List[str]:
        """
        List all available Kafka topics
        
        Returns:
            List of topic names
        """
        try:
            metadata = self.admin_client.describe_cluster()
            topics = list(metadata.topics)
            logger.debug(f"Available topics: {topics}")
            return topics
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            return []
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """
        Send message to Kafka topic
        
        Args:
            topic: Target topic name
            message: Message payload
            key: Optional message key
        """
        try:
            producer = self.get_producer()
            future = producer.send(topic, value=message, key=key)
            result = future.get(timeout=10)
            logger.info(f"Message sent to topic '{topic}': {result}")
        except Exception as e:
            logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise
    
    def close(self):
        """Close all Kafka connections"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
        if self.admin_client:
            self.admin_client.close()
            logger.info("Kafka admin client closed")


# Global Kafka client instance
kafka_client = KafkaClient()
