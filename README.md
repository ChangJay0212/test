# 🚀 Agentic Teaching System

A containerized AI teaching system built with Python and Kafka that creates an intelligent multi-agent teaching team. Students can ask questions and receive responses from specialized AI teacher agents powered by **local Ollama** or cloud-based **Gemini** LLM engines.

## 🏗️ Architecture

```
Student (Producer) → Kafka Topics → AI Teacher Agents (Consumers) → Results Topic → Student
                         ↓
                  Dynamic Assignment (LLM)
                         ↓
              [English Teacher] [Chinese Teacher]
                         ↓
                  [Ollama/Gemini + Tools]
```

### 🧩 Components

- **🎯 Dynamic Assignment**: Smart routing using LLM to select the best teacher
- **📚 Teacher Agents**: Specialized AI teachers (English & Chinese)
- **🔧 LLM Engines**: Support for **Ollama** (local, free) and **Gemini** (cloud-based)
- **🔍 Tool System**: Web search and extensible tool framework
- **📨 Kafka**: Reliable message broker for distributed communication
- **🏥 Health Monitoring**: Comprehensive system health checks
- **📊 Agent Registry**: Dynamic agent management and discovery

## ⚡ Quick Start

### 📋 Prerequisites

- ✅ **Docker** and **Docker Compose** installed
- 🐳 **4GB+ RAM** available for containers
- 🔑 **Google Gemini API key** (optional, for cloud LLM)
- 🦙 **Ollama** (optional, for local LLM - **recommended for privacy**)

### 🚀 Installation & Setup

#### Option 1: 🦙 **Ollama Setup (Recommended - Free & Private)**

1. **Clone project**
   ```bash
   git clone <repository>
   cd agentic_system
   ```

2. **Install Ollama** (if not already installed)
   ```bash
   # Windows: Download from https://ollama.ai
   # Linux/macOS:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Start Ollama and download model**
   ```bash
   ollama serve  # Start Ollama service
   ollama pull llama2  # Download Llama2 model (3.8GB)
   ```

4. **Start the AI teaching system**
   ```bash
   # Windows
   .\start-ollama.bat
   
   # Linux/macOS  
   docker-compose -f docker-compose.ollama.yml up -d --build
   ```

#### Option 2: 🌩️ **Gemini Setup (Cloud-based)**

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   GEMINI_API_KEY=your_gemini_api_key_here
   DEFAULT_LLM_ENGINE=gemini
   ```

2. **Start system**
   ```bash
   docker-compose up -d --build
   ```

### 🧪 **Testing & Verification**

After starting the system, verify everything works:

#### 🔍 **1. Quick Health Check**
```bash
# Windows
.\quick-test.bat

# Linux/macOS
./quick-test.sh
```

**Expected output:**
```
✅ All containers running
✅ Kafka healthy  
✅ Ollama healthy (if using Ollama)
✅ LLM engine connected
✅ Agents responding
```

#### 🗣️ **2. Interactive Testing**
```bash
# Windows - Use the recommended chat interface
.\chat.bat

# Alternative options if needed:
.\interactive-test-fixed.bat   # Full test menu
.\simple-chat.bat             # Minimal interface
.\interactive-simple.bat      # Corrected original

# Linux/macOS  
./interactive-test.sh
```

**Try these test questions:**
```
Your question: What is the difference between "their", "there", and "they're"?
Your question: chinese: 什麼是成語？請給我幾個例子。
Your question: english: How can I improve my writing skills?
Your question: 解釋一下李白的《靜夜思》
```

#### 📊 **3. Check Container Status**
```bash
docker ps
```

**All containers should show "Up" status:**
```
CONTAINER ID   IMAGE                    STATUS
xxxxx          agentic-app             Up X minutes          
xxxxx          ollama                  Up X minutes (healthy)
xxxxx          kafka                   Up X minutes (healthy)  
xxxxx          zookeeper               Up X minutes
```

## 💬 Usage Guide

### 🎯 **Interactive Mode**

After successful startup, use any of these interactive testing options:

```bash
# Windows - Multiple options available

# RECOMMENDED: Simple and reliable chat interface
.\chat.bat

# Alternative options:
.\interactive-test-fixed.bat   # Full-featured test menu
.\simple-chat.bat             # Minimal chat mode  
.\interactive-simple.bat      # Corrected original

# Linux/macOS
./interactive-test.sh
```

### 📝 **Example Conversations**

#### English Teaching Examples:
```
Your question: What is the difference between affect and effect?
🤖 English Teacher: "Affect" is typically a verb meaning to influence...

Your question: english: How do I write a compelling introduction?
🤖 English Teacher: A compelling introduction should hook the reader...

Your question: Can you explain Shakespeare's use of imagery in Macbeth?
🤖 English Teacher: Shakespeare uses vivid imagery throughout Macbeth...
```

#### Chinese Teaching Examples:
```
Your question: chinese: 什麼是成語？
🤖 Chinese Teacher: 成語是中國傳統文化中的固定詞語組合...

Your question: 請解釋李白的《靜夜思》
🤖 Chinese Teacher: 《靜夜思》是李白的經典作品，表達了詩人的思鄉之情...

Your question: 中文: 「有志者事竟成」是什麼意思？
🤖 Chinese Teacher: 這句話的意思是有決心和毅力的人...
```

#### Auto-Detection Examples:
```
Your question: What are some common English grammar mistakes?
🤖 System: Routing to English Teacher...
🤖 English Teacher: Common grammar mistakes include...

Your question: 中國古典詩詞的特點是什麼？
🤖 System: Routing to Chinese Teacher...  
🤖 Chinese Teacher: 中國古典詩詞有以下特點...
```

### 🎮 **Commands & Controls**

| Command | Function |
|---------|----------|
| `quit` or `exit` | Exit interactive mode |
| `status` | Show system health status |
| `english: <question>` | Send directly to English teacher |
| `chinese: <question>` | Send directly to Chinese teacher |
| `中文: <question>` | Send directly to Chinese teacher |
| `help` | Show available commands |

### 🔧 **System Management**

#### Start System:
```bash
# Ollama (local AI)
.\start-ollama.bat              # Windows
docker-compose -f docker-compose.ollama.yml up -d  # Linux/macOS

# Gemini (cloud AI)  
docker-compose up -d            # All platforms
```

#### Stop System:
```bash
# Ollama
docker-compose -f docker-compose.ollama.yml down

# Gemini
docker-compose down
```

#### View Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker logs agentic-app -f
docker logs ollama -f
docker logs kafka -f
```

#### System Status:
```bash
# Container status
docker ps

# Health check
.\quick-test.bat  # Windows
./quick-test.sh   # Linux/macOS
```

## Architecture Details

### Message Flow

1. **Question Submission**: Student sends question via Producer
2. **Dynamic Assignment**: If no specific agent requested, LLM determines best teacher
3. **Agent Processing**: Appropriate teacher agent processes question using LLM + tools
4. **Response Delivery**: Result sent back to student via Results topic

### Agent Framework

**Base Agent** (Abstract)
- LLM engine integration
- Tool management  
- Message processing interface

**Specialized Teachers**
- **English Teacher**: Grammar, writing, literature
- **Chinese Teacher**: Chinese language, literature, culture

### Tool System

**Base Tool** (Abstract)
- Parameter validation
- Execution interface
- Schema definition

**Web Search Tool**
- Searches for additional information
- Formats results for educational context

### LLM Engine

**Base Engine** (Abstract)
- Model initialization
- Response generation
- Tool integration

**Gemini Engine**
- Google Gemini API integration
- Temperature and token controls
- Error handling

**Ollama Engine** 
- Local LLM deployment
- Privacy-focused solution
- No API costs
- Supports various open-source models (Llama 2, Mistral, CodeLlama)

**Engine Factory**
- Automatic engine selection
- Configuration validation
- Fallback mechanisms
- Agent-specific preferences

## System Features

### Health Monitoring
- Kafka cluster status
- Agent connectivity 
- Automatic recovery

### Scalability
- Add new teacher agents easily
- Horizontal scaling with Kafka partitions
- Tool system extensibility

### Reliability
- Message persistence with Kafka
- Retry mechanisms
- Error handling and logging

## Development

### Adding New Agents

1. **Create agent class**:
   ```python
   from agents.base_agent import BaseAgent
   
   class MathTeacherAgent(BaseAgent):
       def process_message(self, message):
           # Implementation
   ```

2. **Register in registry**:
   ```python
   agent_registry.register_agent(AgentInfo(...))
   ```

3. **Add to consumer manager**:
   ```python
   # Add to initialize_agents() method
   ```

### Adding New Tools

1. **Create tool class**:
   ```python
   from tools.base_tool import BaseTool
   
   class CalculatorTool(BaseTool):
       def execute(self, **kwargs):
           # Implementation
   ```

2. **Add to agent**:
   ```python
   agent.add_tool(CalculatorTool())
   ```

### Adding New LLM Engines

1. **Implement base engine**:
   ```python
   from llm_engines.base_engine import BaseLLMEngine
   
   class OpenAIEngine(BaseLLMEngine):
       # Implementation
   ```

## Configuration

Key settings in `config/settings.py`:

- Kafka connection parameters
- Topic names
- LLM model settings  
- Health check intervals
- Logging configuration

## Monitoring

View logs:
```bash
docker-compose logs -f agentic-app
```

Check Kafka topics:
```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

## API Documentation

### Message Format

**Student Question**:
```json
{
  "message": "What is photosynthesis?",
  "producer_uuid": "student_123",
  "request_id": "req_456",
  "timestamp": 1640995200
}
```

**Agent Response**:
```json
{
  "success": true,
  "response": "Photosynthesis is...",
  "agent_type": "english_teacher", 
  "agent_uuid": "english_001",
  "producer_uuid": "student_123",
  "request_id": "req_456",
  "tools_used": ["web_search"]
}
```

## 🧪 Testing & Validation

### 🚀 **Quick Test Suite**

Execute the comprehensive test to verify all components:

```bash
# Windows
.\quick-test.bat

# Linux/macOS  
./quick-test.sh
```

**Test Results Should Show:**
```
🔍 Agentic Teaching System - Health Check
✅ 1. Docker containers running
✅ 2. LLM engine configuration verified  
✅ 3. LLM engine connectivity test passed
✅ 4. English teacher agent responding
✅ 5. Chinese teacher agent responding  
✅ 6. Kafka message flow working
✅ 7. System health check complete
```

### 🔬 **Manual Testing Steps**

1. **Test LLM Engine**:
   ```bash
   docker exec agentic-app python -c "
   from llm_engines.factory import LLMEngineFactory
   engine = LLMEngineFactory.create_for_agent(agent_type='english_teacher')
   print(f'✅ Engine: {type(engine).__name__} with model: {engine.model_name}')
   "
   ```

2. **Test Agent Response**:
   ```bash
   # Start interactive mode
   .\interactive-test.bat
   
   # Try a simple question
   Your question: Hello, can you help me with English?
   ```

3. **Test Dynamic Assignment**:
   ```bash
   # Mixed language questions to test auto-routing
   Your question: What is photosynthesis?        # Should go to English teacher
   Your question: 什麼是光合作用？                  # Should go to Chinese teacher
   ```

### 📊 **Performance Verification**

Monitor system performance:

```bash
# Check response times
docker logs agentic-app | grep "Response time"

# Monitor resource usage  
docker stats

# Check Kafka message flow
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic result --from-beginning
```

### 🐛 **Troubleshooting Guide**

#### Common Issues & Solutions:

1. **🚨 Containers not starting**
   ```bash
   # Check Docker resources
   docker system df
   docker system prune  # Clean up if needed
   
   # Restart with clean state
   docker-compose down
   docker-compose up -d --build
   ```

2. **🚨 Ollama model not found**
   ```bash
   # Check available models
   docker exec ollama ollama list
   
   # Pull model if missing
   docker exec ollama ollama pull llama2
   ```

3. **🚨 LLM engine connection failed**
   ```bash
   # Test Ollama connectivity
   docker exec agentic-app curl http://ollama:11434/api/tags
   
   # Check environment variables
   docker exec agentic-app env | grep OLLAMA
   ```

4. **🚨 No agent responses**
   ```bash
   # Check agent logs
   docker logs agentic-app | grep "agent processing"
   
   # Verify Kafka topics
   docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

#### 📞 **Support Scripts**

The system includes helper scripts for troubleshooting:

```bash
# Windows
.\fix-kafka.bat           # Fix Kafka configuration issues  
.\start-simple.bat        # Simplified startup for compatibility
.\status-check.bat        # System status verification

# Cross-platform
docker-compose logs       # View all service logs
docker ps                 # Check container status
docker exec agentic-app python -c "import sys; print(sys.version)"  # Python version
```

## 🏭 Production Considerations

### 🔧 **Deployment Checklist**

- ✅ Scale Kafka partitions for high throughput
- ✅ Implement proper authentication & authorization  
- ✅ Add monitoring dashboards (Prometheus/Grafana)
- ✅ Set up centralized logging (ELK stack)
- ✅ Configure backup strategies for persistent data
- ✅ Implement rate limiting and throttling
- ✅ Set up SSL/TLS for secure communication
- ✅ Configure resource limits and health checks

### 📈 **Scaling Guidelines**

**Horizontal Scaling:**
```bash
# Scale agents
docker-compose up -d --scale agentic-app=3

# Add Kafka partitions
docker exec kafka kafka-topics --alter --topic english_teacher --partitions 5 --bootstrap-server localhost:9092
```

**Resource Requirements:**
- **Small Setup**: 2 CPU, 4GB RAM (1-10 concurrent users)
- **Medium Setup**: 4 CPU, 8GB RAM (10-50 concurrent users)  
- **Large Setup**: 8+ CPU, 16GB+ RAM (50+ concurrent users)

### 🛡️ **Security Best Practices**

1. **API Keys**: Store in secrets management system
2. **Network**: Use VPN or private networks in production
3. **Authentication**: Implement user authentication for API access
4. **Data Privacy**: Enable Ollama for sensitive/private deployments
5. **Monitoring**: Set up alerts for suspicious activity

## 🐛 Troubleshooting

### 🚨 **Common Issues**

#### ❌ **Problem: Batch file encoding issues (Chinese characters garbled)**
```bash
# Symptoms: Garbled text, commands not recognized
# Example: '?敹恍摨瑟炎??' 不是內部或外部命令

# Solution: Use fixed versions without Unicode issues
.\interactive-test-fixed.bat    # Fixed full-featured version
.\simple-chat.bat              # Simple chat interface
.\interactive-simple.bat       # Corrected original version

# Alternative: Set console encoding
chcp 65001
.\interactive-test.bat
```

#### ❌ **Problem: Kafka connection errors**
```bash
# Solution: Check if Kafka is running and accessible
docker ps | grep kafka
docker logs kafka

# Fix: Restart Kafka services
docker-compose restart kafka zookeeper
```

#### ❌ **Problem: API key errors (Gemini)**
```bash
# Solution: Verify GEMINI_API_KEY in .env file  
docker exec agentic-app env | grep GEMINI_API_KEY

# Fix: Update .env file and restart
docker-compose restart agentic-app
```

#### ❌ **Problem: No responses from agents**
```bash
# Solution: Check agent consumer logs for errors
docker logs agentic-app | grep "agent processing"

# Fix: Restart the system
docker-compose down && docker-compose up -d
```

#### ❌ **Problem: Slow responses**  
```bash
# Solution: Monitor LLM API rate limits and response times
docker logs agentic-app | grep "Response time"

# Fix: Switch to local Ollama for faster responses
# Edit .env: DEFAULT_LLM_ENGINE=ollama
```

#### ❌ **Problem: Ollama model not found**
```bash
# Solution: Check available models
docker exec ollama ollama list

# Fix: Pull the required model
docker exec ollama ollama pull llama2
```

### 🔍 **Debugging Commands**

```bash
# Check Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Monitor message flow
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic result --from-beginning

# View container logs  
docker-compose logs agentic-app
docker-compose logs ollama
docker-compose logs kafka

# Check health status in interactive mode
.\interactive-test.bat
# Then type: status

# Test individual components
docker exec agentic-app python -c "from llm_engines.factory import LLMEngineFactory; print('LLM OK')"
```

### 📚 **Useful Resources**

- **Ollama Models**: https://ollama.ai/models
- **Docker Troubleshooting**: https://docs.docker.com/engine/troubleshooting/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **System Logs**: `./logs/` directory in the project

### 🆘 **Getting Help**

1. **Check this README** for common solutions
2. **Review `trouble.txt`** for detailed troubleshooting history  
3. **Run diagnostic scripts**:
   ```bash
   .\quick-test.bat        # Health check
   .\status-check.bat      # System status
   ```
4. **Check container logs** for specific error messages
5. **Verify system requirements** and dependencies

---

## 📋 **Quick Reference**

### 🚀 **Essential Commands**
```bash
# Start system (Ollama)
.\start-ollama.bat

# Test system  
.\quick-test.bat

# Interactive chat (RECOMMENDED - No encoding issues)
.\chat.bat                     # Best option - simple and reliable

# Alternative interactive modes
.\interactive-test-fixed.bat    # Full-featured version
.\simple-chat.bat              # Minimal chat interface
.\interactive-simple.bat       # Corrected original

# Check status
docker ps
docker-compose logs -f

# Stop system
docker-compose -f docker-compose.ollama.yml down
```

### 📁 **Important Files**
- `docker-compose.ollama.yml` - Ollama deployment configuration
- `docker-compose.yml` - Gemini deployment configuration  
- `.env` - Environment variables and API keys
- `trouble.txt` - Detailed troubleshooting guide
- `ENCODING_FIX.md` - Windows encoding issues solution
- `TEST_RESULTS.md` - Latest testing results and validation
- `README.md` - This comprehensive guide

### 🔗 **Useful Links**
- **Ollama**: https://ollama.ai
- **Google Gemini**: https://ai.google.dev
- **Docker**: https://docker.com
- **Kafka**: https://kafka.apache.org

---

*Last Updated: 2025-07-27*  
*System Version: Agentic Teaching System v2.0 with Ollama Support*
