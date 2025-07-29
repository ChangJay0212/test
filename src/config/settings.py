"""
Configuration settings for the agentic system
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_GROUP = "agentic_system_group"
KAFKA_AUTO_OFFSET_RESET = "earliest"

# Topics
TOPIC_ENGLISH_TEACHER = "english_teacher"
TOPIC_CHINESE_TEACHER = "chinese_teacher"
TOPIC_DYNAMIC_ASSIGN = "dynamic_assign"
TOPIC_RESULT = "result"
TOPIC_TOKEN_USAGE = "token_usage"  # New topic for LLM engines to send token usage data

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-pro"

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# Health Check Configuration
HEALTH_CHECK_INTERVAL = 10  # seconds (shorter interval for faster initial checks)
KAFKA_HEALTH_TIMEOUT = 10  # seconds
MIN_BROKER_COUNT = 1  # minimum brokers for healthy status

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/agentic_system.log"

# Producer Configuration
PRODUCER_REQUEST_TIMEOUT = 30  # seconds
PRODUCER_RETRY_BACKOFF = 5  # seconds

# Consumer Configuration
CONSUMER_POLL_TIMEOUT = 1.0  # seconds
CONSUMER_MAX_RETRIES = 3

# Cost Management Configuration
# Token cost rates (USD per 1K tokens)

# Gemini pricing configuration
GEMINI_INPUT_COST_PER_1K = float(
    os.getenv("GEMINI_INPUT_COST_PER_1K", "0.0005")
)  # $0.0005 per 1K input tokens
GEMINI_OUTPUT_COST_PER_1K = float(
    os.getenv("GEMINI_OUTPUT_COST_PER_1K", "0.0015")
)  # $0.0015 per 1K output tokens

# Ollama pricing configuration (free but can track computational cost)
OLLAMA_COMPUTE_COST_PER_1K = float(
    os.getenv("OLLAMA_COMPUTE_COST_PER_1K", "0.0")
)  # Free for local deployment

# OpenAI pricing configuration (for future use)
OPENAI_INPUT_COST_PER_1K = float(os.getenv("OPENAI_INPUT_COST_PER_1K", "0.0010"))
OPENAI_OUTPUT_COST_PER_1K = float(os.getenv("OPENAI_OUTPUT_COST_PER_1K", "0.0020"))

# Claude pricing configuration (for future use)
CLAUDE_INPUT_COST_PER_1K = float(os.getenv("CLAUDE_INPUT_COST_PER_1K", "0.0008"))
CLAUDE_OUTPUT_COST_PER_1K = float(os.getenv("CLAUDE_OUTPUT_COST_PER_1K", "0.0024"))

# Cost monitoring settings
COST_ALERT_THRESHOLD = float(
    os.getenv("COST_ALERT_THRESHOLD", "10.0")
)  # Alert when daily cost exceeds this amount
COST_TRACKING_ENABLED = os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true"
