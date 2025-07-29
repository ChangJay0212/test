"""
Interactive service for the Agentic Teaching System (Docker container)
This runs as a persistent service in Docker, handling multiple client sessions
"""

import queue
import signal
import sys
import threading
import time
from typing import Any, Dict, Optional

from src.monitoring.cost_manager import cost_monitor_manager
from src.producer.producer import StudentProducer
from src.tools.web_search import WebSearchTool
from src.utils.logger import logger


class InteractiveService:
    """
    Interactive service that runs persistently in Docker container.
    Manages multiple virtual client sessions and handles continuous interaction.
    """

    def __init__(self):
        self.is_running = False
        self.clients = {}  # Dict of client_id -> ClientSession
        self.command_queue = queue.Queue()
        self.auto_demo_enabled = False
        self.demo_interval = 60  # seconds between auto demos
        self._last_request_id = None  # Track last request to avoid duplicate display
        self._output_lock = threading.Lock()  # Thread safety for output

    def start_service(self):
        """
        Start the interactive service.



        Raises:
            Exception:
                An error occurred while starting the service.
        """
        try:
            logger.info("Starting Interactive Service...")

            # Wait for infrastructure to be ready
            logger.info("Waiting for infrastructure to be ready...")
            time.sleep(15)
            
            # Start cost monitor token usage consumer
            try:
                from src.monitoring.cost_monitor import cost_monitor
                cost_monitor.start_token_usage_consumer()
                logger.info("Cost monitor token usage consumer started")
            except Exception as e:
                logger.warning(f"Failed to start cost monitor token usage consumer: {e}")

            self.is_running = True
            logger.info("Interactive Service started successfully!")

            # Start background threads
            self._start_background_threads()

            # Show service status
            self._show_service_status()

        except Exception as e:
            logger.error(f"Failed to start interactive service: {e}")
            self.stop_service()
            raise

    def stop_service(self):
        """
        Stop the interactive service.


        """
        if not self.is_running:
            return

        logger.info("Stopping Interactive Service...")

        # Stop all client sessions
        for client_id, session in self.clients.items():
            session.disconnect()

        self.is_running = False
        logger.info("Interactive Service stopped")

    def _start_background_threads(self):
        """
        Start background threads for service operations.


        """
        # # Auto demo thread
        # demo_thread = threading.Thread(target=self._auto_demo_loop, daemon=True)
        # demo_thread.start()

        # Status monitoring thread
        status_thread = threading.Thread(target=self._status_monitor_loop, daemon=True)
        status_thread.start()

        # Simulated client interaction thread
        # interaction_thread = threading.Thread(target=self._simulated_interaction_loop, daemon=True)
        # interaction_thread.start()

        # Session cleanup thread
        cleanup_thread = threading.Thread(
            target=self._session_cleanup_loop, daemon=True
        )
        cleanup_thread.start()

        logger.info("Background threads started")

    def _session_cleanup_loop(self):
        """
        Periodically clean up inactive sessions.


        """
        while self.is_running:
            try:
                # Periodic cleanup of inactive sessions
                inactive_sessions = [
                    client_id
                    for client_id, session in self.clients.items()
                    if not session.is_connected
                    and session.last_activity_time < time.time() - 3600  # 1 hour
                ]

                for client_id in inactive_sessions:
                    del self.clients[client_id]
                    logger.info(f"Cleaned up inactive session: {client_id}")

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                time.sleep(60)

    def _auto_demo_loop(self):
        """
        Automatically run demo scenarios periodically.


        """
        while self.is_running:
            try:
                if self.auto_demo_enabled:
                    self._run_auto_demo()
                time.sleep(self.demo_interval)
            except Exception as e:
                logger.error(f"Auto demo error: {e}")
                time.sleep(30)  # Wait before retrying

    def _status_monitor_loop(self):
        """
        Monitor and log service status periodically.


        """
        while self.is_running:
            try:
                active_clients = len(
                    [c for c in self.clients.values() if c.is_connected]
                )
                total_requests = sum(
                    len(c.get_pending_requests())
                    for c in self.clients.values()
                    if c.producer
                )

                logger.info(
                    f"Service Status - Active Clients: {active_clients}, Total Requests: {total_requests}"
                )
                time.sleep(120)  # Log every 2 minutes
            except Exception as e:
                logger.error(f"Status monitor error: {e}")
                time.sleep(60)

    def _simulated_interaction_loop(self):
        """
        Simulate various client interactions for testing.


        """
        questions_pool = [
            ("english", "What's the difference between 'affect' and 'effect'?"),
            ("chinese", "請解釋「知己知彼，百戰百勝」的意思"),
            ("english", "How do I improve my writing skills?"),
            ("chinese", "什麼是詩詞的對仗？"),
            ("english", "Explain the concept of metaphors in literature"),
            ("chinese", "請分析李白的詩歌風格"),
            ("english", "What are the key elements of a good essay?"),
            ("chinese", "中文語法中什麼是賓語前置？"),
        ]

        interaction_count = 0
        while self.is_running:
            try:
                # Create a simulated client every 5 minutes
                if interaction_count % 5 == 0:
                    client_id = f"simulated_client_{interaction_count // 5 + 1}"
                    self._create_client_session(client_id)

                # Send questions from existing clients
                if self.clients:
                    import random

                    client_session = random.choice(list(self.clients.values()))
                    if client_session.is_connected:
                        teacher, question = random.choice(questions_pool)
                        agent_type = f"{teacher}_teacher"
                        request_id = client_session.send_question(question, agent_type)
                        if request_id:
                            logger.info(
                                f"Simulated question sent by {client_session.student_name}: {question[:50]}..."
                            )

                interaction_count += 1
                time.sleep(60)  # Wait 1 minute between interactions

            except Exception as e:
                logger.error(f"Simulated interaction error: {e}")
                time.sleep(30)

    def _run_auto_demo(self):
        """
        Run an automated demo with multiple virtual clients.


        """
        logger.info("Running automated demo...")

        demo_questions = [
            (
                "english",
                "What is the difference between 'their', 'there', and 'they're'?",
            ),
            ("chinese", "What does the Chinese phrase '塞翁失馬' mean?"),
            ("english", "How can I improve my English pronunciation?"),
            ("chinese", "Analyze the poem '靜夜思' by Li Bai"),
        ]

        # Create demo client
        demo_client_id = f"auto_demo_{int(time.time())}"
        demo_session = self._create_client_session(demo_client_id)

        if demo_session and demo_session.connect():
            for i, (teacher, question) in enumerate(demo_questions, 1):
                agent_type = f"{teacher}_teacher"
                request_id = demo_session.send_question(question, agent_type)
                if request_id:
                    logger.info(
                        f"Auto demo {i}/{len(demo_questions)}: {question[:50]}..."
                    )
                time.sleep(5)  # Wait between questions

            logger.info(f"Auto demo completed with {len(demo_questions)} questions")
        else:
            logger.error("Failed to create demo client session")

    def _create_client_session(self, client_id: str):
        """
        Create a new client session.

        Args:
            client_id (str): Unique identifier for the client.

        Returns:
            ClientSession: The created client session.
        """
        session = ClientSession(client_id)
        self.clients[client_id] = session
        logger.info(f"Created client session: {client_id}")
        return session

    def _show_service_status(self):
        """
        Show current service status.


        """
        print("\n" + "=" * 60)
        print("INTERACTIVE SERVICE STATUS")
        print("=" * 60)
        print("🔄 Service Mode: Continuous Operation")
        print(
            "🤖 Auto Demo: Enabled"
            if self.auto_demo_enabled
            else "🤖 Auto Demo: Disabled"
        )
        print(f"⏱️  Demo Interval: {self.demo_interval} seconds")
        print(f"👥 Active Sessions: {len(self.clients)}")
        print("🐳 Running in Docker container")
        print("=" * 60)

    def _show_help(self):
        """
        Show available commands.


        """
        print("\n" + "=" * 50)
        print("INTERACTIVE SERVICE COMMANDS")
        print("=" * 50)
        print("📊 System Commands:")
        print("  status          - Show service status")
        print("  cost            - Show cost dashboard")
        print("  cost report     - Generate cost report")
        print("  cost export     - Export cost data")
        print("  budget <amount> - Set budget alert")
        print()
        print("🤖 Service Commands:")
        print("  demo            - Run manual demo")
        print("  clients         - Show client sessions")
        print("  create <name>   - Create new client session")
        print("  send <question> - Send question via service")
        print()
        print("� Tool Testing:")
        print("  test tools      - Test all available tools")
        print("  force tools <question> - Force tool usage with question")
        print("  list tools      - Show available tools")
        print()
        print("�👥 Direct Questions:")
        print("  english: <question> - Send to English teacher")
        print("  chinese: <question> - Send to Chinese teacher")
        print("  <any question>      - Auto-assign teacher")
        print()
        print("🔧 Control:")
        print("  help            - Show this help")
        print("  quit/exit       - Stop the service")
        print("=" * 50)

    def _show_client_sessions(self):
        """
        Show current client sessions.


        """
        print("\n" + "=" * 50)
        print("CLIENT SESSIONS STATUS")
        print("=" * 50)

        if not self.clients:
            print("📭 No active client sessions")
        else:
            for client_id, session in self.clients.items():
                status_icon = "🟢" if session.is_connected else "🔴"
                last_activity = time.time() - session.last_activity_time
                pending_count = len(session.get_pending_requests())

                print(f"{status_icon} {client_id}")
                print(f"   Connected: {'Yes' if session.is_connected else 'No'}")
                print(f"   Last Activity: {last_activity:.0f}s ago")
                print(f"   Pending Requests: {pending_count}")
                print()

        print("=" * 50)

    def _run_manual_demo(self):
        """
        Run a manual demo on demand.


        """
        print("\n🎬 Running manual demo...")
        self._run_auto_demo()
        print("✅ Manual demo completed!")

    def _send_question_via_service(
        self, question: str, agent_type: Optional[str] = None
    ):
        """
        Send a question via the service using an available client with detailed metrics.

        Args:
            question (str): The question to send.
            agent_type (Optional[str]): Specific agent type to target.


        """
        # Find or create an available client
        available_client = None
        for session in self.clients.values():
            if session.is_connected:
                available_client = session
                break

        if not available_client:
            # Create a new service client
            service_client_id = f"service_client_{int(time.time())}"
            available_client = self._create_client_session(service_client_id)
            if not available_client.connect():
                print("❌ Failed to create service client for sending question")
                return

        # Get initial statistics for cost tracking
        try:
            initial_stats = cost_monitor_manager.get_dashboard_data()
            start_time = time.time()

            # Send the question directly through producer to avoid duplicate output
            request_id = available_client.producer.send_question(question, agent_type, user_id="service_user")

            if request_id:
                # Check if this is a duplicate request display
                with self._output_lock:
                    if self._last_request_id == request_id:
                        # Skip duplicate display
                        teacher_type = (
                            agent_type.replace("_", " ").title() if agent_type else "AI Teacher"
                        )
                        print(f"\n⚡ Duplicate request detected, skipping display for {request_id}")
                    else:
                        self._last_request_id = request_id
                        teacher_type = (
                            agent_type.replace("_", " ").title() if agent_type else "AI Teacher"
                        )
                        print(f"\n✅ Question sent to {teacher_type}!")
                        print(f"📝 Question: {question}")
                        print(f"🆔 Request ID: {request_id}")
                        print(f"� Via Client: {available_client.student_name}")

                        # Wait for response from the actual agent
                        print(f"\n⏳ Waiting for response from {teacher_type}...")

                # Wait for the actual response with detailed information
                response = available_client.producer.wait_for_response(
                    request_id, timeout=15.0
                )

                if response and response.get("success", False):
                    elapsed_time = time.time() - start_time
                    # Display the actual response using the new method
                    self._display_actual_response(response, teacher_type, elapsed_time)
                elif response:
                    # Error response
                    error_msg = response.get("error", "Unknown error")
                    print(f"\n❌ Error from {teacher_type}: {error_msg}")
                else:
                    # Timeout - fallback to cost monitor
                    self._display_fallback_metrics(
                        initial_stats, start_time, teacher_type
                    )

                print("   " + "─" * 40)

            else:
                print("❌ Failed to send question")

        except Exception as e:
            logger.error(f"Error in detailed question sending: {e}")
            print(f"❌ Error: {e}")

    def _handle_send_command(self, command: str):
        """
        Handle 'send <question>' command.

        Args:
            command (str): The send command with question.


        """
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("❌ Usage: send <question>")
            return

        question = parts[1].strip()
        if question:
            self._send_question_via_service(question)
        else:
            print("❌ Please provide a question to send")

    def _handle_create_client_command(self, command: str):
        """
        Handle 'create <client_name>' command.

        Args:
            command (str): The create command with client name.


        """
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("❌ Usage: create <client_name>")
            return

        client_name = parts[1].strip()
        if client_name:
            session = self._create_client_session(client_name)
            if session.connect():
                print(f"✅ Created and connected client session: {client_name}")
            else:
                print(f"❌ Failed to connect client session: {client_name}")
        else:
            print("❌ Please provide a client name")

    def _show_cost_dashboard(self):
        """
        Show cost monitoring dashboard.


        """
        try:
            # Import here to avoid circular imports
            from src.monitoring.cost_manager import cost_monitor_manager

            dashboard_data = cost_monitor_manager.get_dashboard_data()

            print("\n" + "=" * 60)
            print("COST MONITORING DASHBOARD")
            print("=" * 60)

            # System info
            uptime = dashboard_data["system_info"]["uptime_hours"]
            print(f"System Uptime: {uptime:.1f} hours")

            # Cost overview
            overview = dashboard_data["cost_overview"]
            print("\n📊 Cost Overview:")
            print(
                f"Last Hour:     {overview['last_hour']['requests']} requests, ${overview['last_hour']['cost']:.6f}"
            )
            print(
                f"Last 24 Hours: {overview['last_24_hours']['requests']} requests, ${overview['last_24_hours']['cost']:.6f}"
            )
            print(
                f"Last Week:     {overview['last_week']['requests']} requests, ${overview['last_week']['cost']:.6f}"
            )

            # Agent performance
            if dashboard_data["agent_performance"]:
                print("\n🤖 Agent Performance (24h):")
                for agent_type, stats in dashboard_data["agent_performance"].items():
                    print(
                        f"  {agent_type.replace('_', ' ').title()}: "
                        f"{stats['requests']} requests, "
                        f"${stats['cost']:.6f}, "
                        f"{stats['average_response_time']:.2f}s avg"
                    )

            # Alerts
            if dashboard_data["alerts"]:
                print("\n⚠️ Alerts:")
                for alert in dashboard_data["alerts"]:
                    level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(
                        alert["level"], ""
                    )
                    print(f"  {level_icon} {alert['message']}")

            print("=" * 60)

        except Exception as e:
            print(f"❌ Error showing cost dashboard: {e}")

    def _show_cost_report(self):
        """
        Show detailed cost report.


        """
        try:
            from src.monitoring.cost_manager import cost_monitor_manager

            report = cost_monitor_manager.get_cost_report("detailed")
            print(report)
        except Exception as e:
            print(f"❌ Error generating cost report: {e}")

    def _export_cost_data(self):
        """
        Export cost data to file.


        """
        try:
            from src.monitoring.cost_manager import cost_monitor_manager

            filename = cost_monitor_manager.export_data(hours=24)
            print(f"✅ Cost data exported to: {filename}")
        except Exception as e:
            print(f"❌ Error exporting cost data: {e}")

    def _handle_budget_command(self, command: str):
        """
        Handle budget alert command.

        Args:
            command (str): The budget command string containing amount.


        """
        try:
            parts = command.split()
            if len(parts) >= 2:
                budget_amount = float(parts[1])
                from src.monitoring.cost_manager import cost_monitor_manager

                budget_status = cost_monitor_manager.get_budget_alert(budget_amount)

                level_icon = {
                    "error": "🔴",
                    "warning": "🟡",
                    "info": "🔵",
                    "success": "🟢",
                }.get(budget_status["level"], "")
                print(f"\n{level_icon} Budget Status: {budget_status['message']}")
                print(f"Remaining budget: ${budget_status['remaining_budget']:.6f}")
            else:
                print("❌ Usage: budget <amount> (e.g., 'budget 5.00')")
        except ValueError:
            print("❌ Invalid budget amount. Please enter a number.")
        except Exception as e:
            print(f"❌ Error checking budget: {e}")

    def _test_all_tools(self):
        """
        Test all available tools to ensure they're working correctly.


        """
        print("\n" + "=" * 60)
        print("TESTING ALL AVAILABLE TOOLS")
        print("=" * 60)

        try:
            # Import all tools

            tools_to_test = [
                (
                    WebSearchTool(),
                    "search",
                    {"query": "artificial intelligence", "max_results": 3},
                ),
            ]

            print(f"Found {len(tools_to_test)} tools to test...\n")

            for i, (tool, test_name, test_params) in enumerate(tools_to_test, 1):
                print(f"🔧 Test {i}/{len(tools_to_test)}: {tool.name}")
                print(f"   Description: {tool.description}")
                print(f"   Test Parameters: {test_params}")

                try:
                    result = tool.execute(**test_params)
                    success_icon = "✅" if result.get("success", False) else "❌"
                    print(f"   Result: {success_icon} {result}")

                    if result.get("success", False):
                        print(f"   ✅ Tool '{tool.name}' is working correctly!")
                    else:
                        print(
                            f"   ❌ Tool '{tool.name}' failed: {result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    print(f"   ❌ Tool '{tool.name}' threw exception: {e}")

                print("   " + "-" * 50)

            print("🎯 Tool testing completed!")
            print("=" * 60)

        except Exception as e:
            print(f"❌ Error during tool testing: {e}")

    def _force_tool_usage(self, command: str):
        """
        Force tool usage with a specific question to test tool integration.

        Args:
            command (str): The command containing the question.


        """
        parts = command.split(" ", 2)
        if len(parts) < 3:
            print("❌ Usage: force tools <question>")
            print("📌 Example: force tools What's the weather in Tokyo?")
            return

        question = parts[2].strip()
        if not question:
            print("❌ Please provide a question for tool testing")
            return

        print(f"\n🔧 Force Tool Testing with Question: {question}")
        print("=" * 60)

        # Create a test prompt that explicitly requests tool usage
        enhanced_question = f"""The user is asking: "{question}"

Please use any relevant tools available to provide a comprehensive answer. This is a tool testing scenario, so actively look for opportunities to use tools like:
- Web search for current information

Question: {question}"""

        # Send with English teacher (which has tools configured)
        self._send_question_via_service(enhanced_question, "english_teacher")

    def _list_available_tools(self):
        """
        List all available tools and their descriptions.


        """
        print("\n" + "=" * 60)
        print("AVAILABLE TOOLS")
        print("=" * 60)

        try:
            tools = [WebSearchTool()]

            for i, tool in enumerate(tools, 1):
                print(f"🔧 {i}. {tool.name}")
                print(f"   📝 Description: {tool.description}")

                # Get tool parameters schema if available
                try:
                    if hasattr(tool, "get_parameters_schema"):
                        schema = tool.get_parameters_schema()
                        print(
                            f"   📋 Parameters: {list(schema.get('properties', {}).keys())}"
                        )
                    elif hasattr(tool, "get_tool_definition"):
                        definition = tool.get_tool_definition()
                        print(f"   📋 Definition: {definition}")
                except Exception as e:
                    print(f"   ⚠️  Schema error: {e}")

                print()

            print(f"📊 Total Tools Available: {len(tools)}")
            print("💡 Use 'test tools' to test all tools")
            print("💡 Use 'force tools <question>' to test tool integration")
            print("=" * 60)

        except Exception as e:
            print(f"❌ Error listing tools: {e}")

    def _display_actual_response(
        self, response: Dict[str, Any], teacher_type: str, elapsed_time: float
    ):
        """
        Display actual response from agent with detailed metrics.

        Args:
            response: The response message from the agent
            teacher_type: Type of teacher that responded
            elapsed_time: Time elapsed for the entire request

        """
        # Display the actual response
        with self._output_lock:
            print(f"\n💬 Response from {teacher_type}:")
            response_text = response.get("response", "No response text")

            # Display full response text (no truncation)
            print(f"   📖 Answer: {response_text}")

        # If response is very long, add a separator
        if len(response_text) > 500:
            print(f"\n   {'─' * 60}")

        # Display actual tool usage from response
        tools_used = response.get("tools_used", [])
        tool_results = response.get("tool_results", {})

        if tools_used:
            print(f"\n🔧 Tools Actually Used: {', '.join(tools_used)}")
            for tool_name, tool_result in tool_results.items():
                if tool_result.get("success", False):
                    result_data = tool_result.get(
                        "data", tool_result.get("result", "Success")
                    )
                    # Display more of the tool result (increase from 100 to 300 chars)
                    result_str = str(result_data)
                    if len(result_str) > 300:
                        print(f"   ✅ {tool_name}: {result_str[:300]}...")
                    else:
                        print(f"   ✅ {tool_name}: {result_str}")
                else:
                    error_msg = tool_result.get("error", "Failed")
                    print(f"   ❌ {tool_name}: {error_msg}")
        else:
            print("\n🔧 Tools Used: None")

        # Display actual cost and performance from response
        cost_info = response.get("cost_info", {})
        response_time = response.get("response_time", elapsed_time)
        performance_metrics = response.get("performance_metrics", {})

        print("\n📊 Actual Performance Metrics:")
        print(f"   ⚡ Agent Response Time: {response_time:.2f}s")
        print(f"   ⏱️  Total Elapsed Time: {elapsed_time:.2f}s")

        # Try to get cost information from cost monitor for the request
        request_id = response.get("request_id")
        cost_found = False
        
        if request_id:
            try:
                # Import cost monitor to get recent cost data
                from src.monitoring.cost_monitor import cost_monitor
                
                # Look for cost records from the last few seconds that match this request
                recent_cutoff = time.time() - 10  # Last 10 seconds
                matching_requests = [
                    r for r in cost_monitor.requests 
                    if r.timestamp >= recent_cutoff and r.request_id == request_id
                ]
                
                if matching_requests:
                    # Get the most recent matching request
                    cost_record = matching_requests[-1]
                    
                    input_tokens = cost_record.input_tokens
                    output_tokens = cost_record.output_tokens
                    total_tokens = cost_record.total_tokens
                    total_cost = cost_record.total_cost
                    model_name = cost_record.model_name

                    print(f"   🔢 Input Tokens: {input_tokens}")
                    print(f"   📝 Output Tokens: {output_tokens}")
                    print(f"   🎯 Total Tokens: {total_tokens}")
                    print(f"   💰 Total Cost: ${total_cost:.6f}")
                    print(f"   🤖 Model: {model_name}")

                    if response_time > 0 and total_tokens > 0:
                        tokens_per_second = total_tokens / response_time
                        print(f"   🚀 Tokens/s: {tokens_per_second:.2f}")

                    if total_tokens > 0:
                        cost_per_token = total_cost / total_tokens
                        print(f"   💎 Cost/Token: ${cost_per_token:.8f}")

                    print("   ✅ Real token tracking successful!")
                    cost_found = True
                    
            except Exception as e:
                logger.debug(f"Could not get cost info from cost monitor: {e}")
        
        # Fallback to response cost_info if available (backward compatibility)
        if not cost_found and cost_info:
            input_tokens = cost_info.get("input_tokens", 0)
            output_tokens = cost_info.get("output_tokens", 0)
            total_tokens = cost_info.get("total_tokens", input_tokens + output_tokens)
            total_cost = cost_info.get("total_cost", 0.0)
            model_name = cost_info.get("model_name", "unknown")

            print(f"   🔢 Input Tokens: {input_tokens}")
            print(f"   📝 Output Tokens: {output_tokens}")
            print(f"   🎯 Total Tokens: {total_tokens}")
            print(f"   💰 Total Cost: ${total_cost:.6f}")
            print(f"   🤖 Model: {model_name}")

            if response_time > 0 and total_tokens > 0:
                tokens_per_second = total_tokens / response_time
                print(f"   🚀 Tokens/s: {tokens_per_second:.2f}")

            if total_tokens > 0:
                cost_per_token = total_cost / total_tokens
                print(f"   💎 Cost/Token: ${cost_per_token:.8f}")

            print("   ✅ Real token tracking successful!")
            cost_found = True
        
        # If still no cost info found, show message
        if not cost_found:
            print("   ⚠️  Cost information not yet available (processing via Kafka)")
            print("   ℹ️  Token data is being processed by cost monitor")

        # Show tools count
        tools_count = performance_metrics.get("tools_count", len(tools_used))
        print(f"   🔧 Tools Executed: {tools_count}")

    def _display_fallback_metrics(
        self, initial_stats: Dict, start_time: float, teacher_type: str
    ):
        """
        Display fallback metrics when response times out.

        Args:
            initial_stats: Initial cost statistics
            start_time: Request start time
            teacher_type: Type of teacher

        """
        print(f"\n⏰ Timeout waiting for response from {teacher_type}")
        print("   📊 Fallback Cost Monitor Metrics:")

        try:
            from src.monitoring.cost_manager import cost_monitor_manager

            updated_stats = cost_monitor_manager.get_dashboard_data()
            elapsed_time = time.time() - start_time

            initial_cost = initial_stats.get("cost_overview", {}).get("last_hour", {})
            updated_cost = updated_stats.get("cost_overview", {}).get("last_hour", {})

            cost_diff = updated_cost.get("cost", 0) - initial_cost.get("cost", 0)
            token_diff = updated_cost.get("tokens", 0) - initial_cost.get("tokens", 0)
            request_diff = updated_cost.get("requests", 0) - initial_cost.get(
                "requests", 0
            )

            print(f"   💰 Token Cost: ${cost_diff:.6f}")
            print(f"   🔢 Tokens Used: {token_diff}")
            print(f"   ⚡ Response Time: {elapsed_time:.2f}s")
            print(f"   📦 Requests Processed: {request_diff}")
        except Exception as e:
            print(f"   ❌ Error getting fallback metrics: {e}")

    def keep_alive(self):
        """
        Keep the service running with interactive command interface.


        """
        logger.info("Interactive Service is running with command interface...")
        print("🔄 Interactive Service is now running with command interface.")
        print("� You can enter commands to interact with the system.")
        print("📊 Available commands: status, cost, demo, clients, help, quit")
        print("⏹️  Type 'quit' or press Ctrl+C to stop the service.")

        try:
            while self.is_running:
                try:
                    user_input = input("\nService command: ").strip()

                    if user_input.lower() in ["quit", "exit"]:
                        break
                    elif user_input.lower() == "status":
                        self._show_service_status()
                        continue
                    elif user_input.lower() == "cost":
                        self._show_cost_dashboard()
                        continue
                    elif user_input.lower() == "cost report":
                        self._show_cost_report()
                        continue
                    elif user_input.lower() == "cost export":
                        self._export_cost_data()
                        continue
                    elif user_input.lower().startswith("budget "):
                        self._handle_budget_command(user_input)
                        continue
                    elif user_input.lower() == "demo":
                        self._run_manual_demo()
                        continue
                    elif user_input.lower() == "clients":
                        self._show_client_sessions()
                        continue
                    elif user_input.lower() == "help":
                        self._show_help()
                        continue
                    elif user_input.lower().startswith("send "):
                        self._handle_send_command(user_input)
                        continue
                    elif user_input.lower().startswith("create "):
                        self._handle_create_client_command(user_input)
                        continue
                    elif user_input.lower() == "test tools":
                        self._test_all_tools()
                        continue
                    elif user_input.lower().startswith("force tools "):
                        self._force_tool_usage(user_input)
                        continue
                    elif user_input.lower() == "list tools":
                        self._list_available_tools()
                        continue
                    elif not user_input:
                        continue

                    # Check for specific agent requests
                    agent_type = None
                    if user_input.startswith("english:"):
                        agent_type = "english_teacher"
                        user_input = user_input[8:].strip()
                    elif user_input.startswith("chinese:"):
                        agent_type = "chinese_teacher"
                        user_input = user_input[8:].strip()

                    # Since all messages go through dynamic_assign.py anyway,
                    # just send any non-empty input as a question
                    if user_input:
                        self._send_question_via_service(user_input, agent_type)
                    else:
                        print(
                            "❓ Please enter a question or command. Type 'help' for available commands."
                        )

                except EOFError:
                    break
                except Exception as e:
                    logger.error(f"Command processing error: {e}")
                    print(f"❌ Error processing command: {e}")

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")

        finally:
            self.stop_service()


class ClientSession:
    """
    Represents a virtual client session within the service.
    """

    def __init__(self, student_name: str):
        """
        Initialize a client session.

        Args:
            student_name (str): Name/ID of the student.
        """
        self.student_name = student_name
        self.producer = None
        self.is_connected = False
        self.last_activity_time = time.time()

    def connect(self) -> bool:
        """
        Connect the client session to the system.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            logger.info(f"Connecting client session: {self.student_name}")
            self.producer = StudentProducer(self.student_name)
            self.producer.start_result_listener()
            self.is_connected = True
            self.last_activity_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Failed to connect session {self.student_name}: {e}")
            return False

    def disconnect(self):
        """
        Disconnect the client session.


        """
        if self.producer:
            self.producer.stop_result_listener()
            self.producer = None
        self.is_connected = False
        logger.info(f"Disconnected client session: {self.student_name}")

    def send_question(
        self, question: str, agent_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Send a question through this client session with detailed cost tracking.

        Args:
            question (str): The question to send.
            agent_type (Optional[str]): Specific agent type to target.

        Returns:
            Optional[str]: Request ID if successful, None otherwise.
        """
        if not self.is_connected or not self.producer:
            return None

        try:
            # Record start time for performance measurement
            start_time = time.time()

            # Send the question
            request_id = self.producer.send_question(question, agent_type)

            if request_id:
                # Track request details
                self.last_activity_time = time.time()

                # Get initial cost statistics

                initial_stats = cost_monitor_manager.get_dashboard_data()

                # Display request information
                teacher_type = (
                    agent_type.replace("_", " ").title()
                    if agent_type
                    else "Auto-assigned"
                )
                print("\n📤 Request Sent:")
                print(f"   🎯 Target: {teacher_type}")
                print(
                    f"   📝 Question: {question[:80]}{'...' if len(question) > 80 else ''}"
                )
                print(f"   🆔 Request ID: {request_id}")
                print(
                    f"   ⏰ Timestamp: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
                )

                # Wait a moment to get updated statistics
                print("   ⏳ Waiting for cost statistics to update...")
                time.sleep(8)  # Increased wait time for proper cost tracking

                # Get updated statistics and calculate cost
                updated_stats = cost_monitor_manager.get_dashboard_data()
                self._display_request_metrics(initial_stats, updated_stats, start_time)

            return request_id

        except Exception as e:
            logger.error(f"Failed to send question from {self.student_name}: {e}")
            return None

    def _display_request_metrics(
        self, initial_stats: Dict, updated_stats: Dict, start_time: float
    ):
        """
        Display detailed metrics for the request.

        Args:
            initial_stats (Dict): Statistics before request.
            updated_stats (Dict): Statistics after request.
            start_time (float): Request start timestamp.


        """
        try:
            # Calculate time elapsed
            elapsed_time = time.time() - start_time
            request_per_second = 1.0 / elapsed_time if elapsed_time > 0 else 0

            # Extract cost information
            initial_cost = initial_stats.get("cost_overview", {}).get("last_hour", {})
            updated_cost = updated_stats.get("cost_overview", {}).get("last_hour", {})

            # Calculate incremental costs
            cost_diff = updated_cost.get("cost", 0) - initial_cost.get("cost", 0)
            token_diff = updated_cost.get("tokens", 0) - initial_cost.get("tokens", 0)
            request_diff = updated_cost.get("requests", 0) - initial_cost.get(
                "requests", 0
            )

            # Display metrics
            print("\n📊 Request Metrics:")
            print(f"   💰 Token Cost: ${cost_diff:.6f}")
            print(f"   🔢 Tokens Used: {token_diff}")
            print(f"   ⚡ Response Time: {elapsed_time:.2f}s")
            print(f"   📈 Request/s: {request_per_second:.2f}")
            print(f"   📦 Total Requests: {request_diff}")

            # Debug information
            print("\n🔍 Statistics Debug:")
            print(
                f"   Before - Requests: {initial_cost.get('requests', 0)}, Tokens: {initial_cost.get('tokens', 0)}"
            )
            print(
                f"   After  - Requests: {updated_cost.get('requests', 0)}, Tokens: {updated_cost.get('tokens', 0)}"
            )
            print(f"   Change - Requests: +{request_diff}, Tokens: +{token_diff}")

            # Calculate cost per token if available
            if token_diff > 0:
                cost_per_token = cost_diff / token_diff if cost_diff > 0 else 0
                print(f"   💎 Cost/Token: ${cost_per_token:.8f}")
                print("   ✅ Cost tracking successful!")
            else:
                print("   ⚠️  No tokens recorded in cost monitor yet")

            # Display efficiency metrics
            if elapsed_time > 0 and token_diff > 0:
                tokens_per_second = token_diff / elapsed_time
                print(f"   🚀 Tokens/s: {tokens_per_second:.2f}")

            print("   " + "─" * 40)

        except Exception as e:
            logger.error(f"Error displaying request metrics: {e}")
            print(f"   ⚠️ Metrics calculation error: {e}")

    def get_pending_requests(self) -> Dict[str, Any]:
        """
        Get pending requests for this session.

        Returns:
            Dict[str, Any]: Pending requests information.
        """
        if not self.producer:
            return {}

        try:
            return self.producer.get_pending_requests()
        except Exception:
            return {}


def signal_handler(signum, frame):
    """
    Handle shutdown signals.

    Args:
        signum: Signal number.
        frame: Current stack frame.

    Returns:
        None
    """
    print("\nReceived shutdown signal. Stopping interactive service...")
    if "service" in globals():
        service.stop_service()
    sys.exit(0)


def main():
    """
    Main function for running the interactive service in Docker.

    Returns:
        None

    Raises:
        KeyboardInterrupt:
            When service is interrupted by user.
        Exception:
            An error occurred during service execution.
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🐳 Starting Interactive Service in Docker Container")
    print("=" * 60)

    # Create and start service
    global service
    service = InteractiveService()

    try:
        # Start the interactive service
        service.start_service()

        # Keep the service alive
        service.keep_alive()

    except KeyboardInterrupt:
        print("\nInteractive service interrupted by user")
    except Exception as e:
        logger.error(f"Interactive service error: {e}")
        print(f"Interactive service error: {e}")
    finally:
        service.stop_service()
        print("Interactive service shutdown complete.")


if __name__ == "__main__":
    main()
