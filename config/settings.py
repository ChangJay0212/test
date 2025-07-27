"""
Configuration settings for the agentic system
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_CONSUMER_GROUP = 'agentic_system_group'
KAFKA_AUTO_OFFSET_RESET = 'earliest'

# Topics
TOPIC_ENGLISH_TEACHER = 'english_teacher'
TOPIC_CHINESE_TEACHER = 'chinese_teacher'
TOPIC_DYNAMIC_ASSIGN = 'dynamic_assign'
TOPIC_RESULT = 'result'

# LLM Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-pro'

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '60'))

# Health Check Configuration
HEALTH_CHECK_INTERVAL = 30  # seconds
KAFKA_HEALTH_TIMEOUT = 10   # seconds

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/agentic_system.log'

# Producer Configuration
PRODUCER_REQUEST_TIMEOUT = 30  # seconds
PRODUCER_RETRY_BACKOFF = 5     # seconds

# Consumer Configuration
CONSUMER_POLL_TIMEOUT = 1.0    # seconds
CONSUMER_MAX_RETRIES = 3
