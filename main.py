"""
Main entry point for the agentic system with cost monitoring
"""
import time
import signal
import sys
from core.logger import logger
from core.health_check import health_checker
from core.cost_manager import cost_monitor_manager
from consumer.consumer_manager import consumer_manager
from producer.producer import StudentProducer


class AgenticSystem:
    """
    Main agentic system orchestrator
    """
    
    def __init__(self):
        self.is_running = False
        self.producer = None
        
    def start_system(self):
        """Start the complete agentic system"""
        try:
            logger.info("Starting Agentic Teaching System...")
            
            # Add startup delay to ensure all infrastructure services are ready
            logger.info("Waiting for infrastructure services to be ready...")
            time.sleep(10)  # Give Kafka and Ollama time to fully initialize
            
            # Start health monitoring
            health_checker.start_monitoring()
            
            # Initialize and start consumers (agents)
            logger.info("Initializing agents...")
            consumer_manager.initialize_agents()
            
            logger.info("Starting agent consumers...")
            consumer_manager.start_all_consumers()
            
            # Wait a moment for consumers to start
            time.sleep(3)
            
            # Create and start producer for demo
            logger.info("Starting student producer...")
            self.producer = StudentProducer("demo_student_001")
            self.producer.start_result_listener()
            
            self.is_running = True
            logger.info("Agentic Teaching System started successfully!")
            
            # Show system status
            self._show_system_status()
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            self.stop_system()
            raise
    
    def stop_system(self):
        """Stop the agentic system"""
        if not self.is_running:
            return
            
        logger.info("Stopping Agentic Teaching System...")
        
        # Stop producer
        if self.producer:
            self.producer.stop_result_listener()
        
        # Stop consumers
        consumer_manager.stop_all_consumers()
        
        # Stop health monitoring
        health_checker.stop_monitoring()
        
        self.is_running = False
        logger.info("Agentic Teaching System stopped")
    
    def _show_system_status(self):
        """Show current system status"""
        print("\n" + "="*60)
        print("AGENTIC TEACHING SYSTEM STATUS")
        print("="*60)
        
        # Health status
        health_status = health_checker.get_system_health()
        print(f"Kafka Status: {health_status['kafka']}")
        print(f"Registered Agents: {health_status['registered_agents']}")
        
        # Consumer status
        consumer_status = consumer_manager.get_consumer_status()
        print("\nActive Agents:")
        for agent_uuid, status in consumer_status.items():
            running_status = "Running" if status['is_running'] else "Stopped"
            print(f"  - {status['agent_type']}: {running_status} (Messages: {status['message_count']})")
        
        print("="*60)
    
    def run_demo(self):
        """Run a demonstration of the system"""
        if not self.is_running:
            logger.error("System not running. Start system first.")
            return
        
        print("\n" + "="*60)
        print("RUNNING DEMO - SENDING SAMPLE QUESTIONS")
        print("="*60)
        
        # Send sample questions
        demo_questions = [
            "What is the difference between 'their', 'there', and 'they're'?",
            "Can you explain the symbolism in Shakespeare's Macbeth?",
            "What does the Chinese phrase '塞翁失馬' mean?",
            "How can I improve my English pronunciation?",
            "Analyze the poem '靜夜思' by Li Bai",
            "What are some common English grammar mistakes to avoid?"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. Sending: {question}")
            request_id = self.producer.send_question(question)
            if request_id:
                print(f"   Request ID: {request_id}")
            else:
                print("   Failed to send question")
            time.sleep(3)  # Wait between questions
        
        print(f"\nSent {len(demo_questions)} questions. Waiting for responses...")
        
        # Wait for responses
        time.sleep(20)
        
        # Show pending requests
        pending = self.producer.get_pending_requests()
        completed = sum(1 for req in pending.values() if req['status'] == 'completed')
        print(f"\nDemo completed: {completed}/{len(pending)} responses received")
    
    def run_interactive_mode(self):
        """Run interactive mode for manual testing"""
        if not self.is_running:
            logger.error("System not running. Start system first.")
            return
        
        print("\n" + "="*60)
        print("INTERACTIVE MODE - TYPE YOUR QUESTIONS")
        print("Commands:")
        print("  'quit' or 'exit' - Exit interactive mode")
        print("  'status' - Show system status")
        print("  'cost' - Show cost monitoring dashboard")
        print("  'cost report' - Generate detailed cost report")
        print("  'cost export' - Export cost data to file")
        print("  'budget <amount>' - Set daily budget alert (e.g., 'budget 5.00')")
        print("  'english:' - Send to English teacher specifically")
        print("  'chinese:' - Send to Chinese teacher specifically")
        print("="*60)
        
        try:
            while True:
                user_input = input("\nYour question: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'status':
                    self._show_system_status()
                    continue
                elif user_input.lower() == 'cost':
                    self._show_cost_dashboard()
                    continue
                elif user_input.lower() == 'cost report':
                    self._show_cost_report()
                    continue
                elif user_input.lower() == 'cost export':
                    self._export_cost_data()
                    continue
                elif user_input.lower().startswith('budget '):
                    self._handle_budget_command(user_input)
                    continue
                elif not user_input:
                    continue
                
                # Check for specific agent requests
                agent_type = None
                if user_input.startswith('english:'):
                    agent_type = 'english_teacher'
                    user_input = user_input[8:].strip()
                elif user_input.startswith('chinese:'):
                    agent_type = 'chinese_teacher'
                    user_input = user_input[8:].strip()
                
                if user_input:
                    request_id = self.producer.send_question(user_input, agent_type)
                    if request_id:
                        print(f"Question sent! Request ID: {request_id}")
                    else:
                        print("Failed to send question.")
                
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
    
    def _show_cost_dashboard(self):
        """Show cost monitoring dashboard"""
        try:
            dashboard_data = cost_monitor_manager.get_dashboard_data()
            
            print("\n" + "="*60)
            print("COST MONITORING DASHBOARD")
            print("="*60)
            
            # System info
            uptime = dashboard_data["system_info"]["uptime_hours"]
            print(f"System Uptime: {uptime:.1f} hours")
            
            # Cost overview
            overview = dashboard_data["cost_overview"]
            print(f"\n📊 Cost Overview:")
            print(f"Last Hour:     {overview['last_hour']['requests']} requests, ${overview['last_hour']['cost']:.6f}")
            print(f"Last 24 Hours: {overview['last_24_hours']['requests']} requests, ${overview['last_24_hours']['cost']:.6f}")
            print(f"Last Week:     {overview['last_week']['requests']} requests, ${overview['last_week']['cost']:.6f}")
            
            # Agent performance
            if dashboard_data["agent_performance"]:
                print(f"\n🤖 Agent Performance (24h):")
                for agent_type, stats in dashboard_data["agent_performance"].items():
                    print(f"  {agent_type.replace('_', ' ').title()}: "
                          f"{stats['requests']} requests, "
                          f"${stats['cost']:.6f}, "
                          f"{stats['average_response_time']:.2f}s avg")
            
            # Alerts
            if dashboard_data["alerts"]:
                print(f"\n⚠️ Alerts:")
                for alert in dashboard_data["alerts"]:
                    level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["level"], "")
                    print(f"  {level_icon} {alert['message']}")
            
            print("="*60)
            
        except Exception as e:
            print(f"Error showing cost dashboard: {e}")
    
    def _show_cost_report(self):
        """Show detailed cost report"""
        try:
            report = cost_monitor_manager.get_cost_report("detailed")
            print(report)
        except Exception as e:
            print(f"Error generating cost report: {e}")
    
    def _export_cost_data(self):
        """Export cost data to file"""
        try:
            filename = cost_monitor_manager.export_data(hours=24)
            print(f"Cost data exported to: {filename}")
        except Exception as e:
            print(f"Error exporting cost data: {e}")
    
    def _handle_budget_command(self, command: str):
        """Handle budget alert command"""
        try:
            parts = command.split()
            if len(parts) >= 2:
                budget_amount = float(parts[1])
                budget_status = cost_monitor_manager.get_budget_alert(budget_amount)
                
                level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵", "success": "🟢"}.get(budget_status["level"], "")
                print(f"\n{level_icon} Budget Status: {budget_status['message']}")
                print(f"Remaining budget: ${budget_status['remaining_budget']:.6f}")
            else:
                print("Usage: budget <amount> (e.g., 'budget 5.00')")
        except ValueError:
            print("Invalid budget amount. Please enter a number.")
        except Exception as e:
            print(f"Error checking budget: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nReceived shutdown signal. Stopping system...")
    if 'system' in globals():
        system.stop_system()
    sys.exit(0)


def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    global system
    system = AgenticSystem()
    
    try:
        # Start the system
        system.start_system()
        
        # Run demo
        print("\nRunning demonstration...")
        system.run_demo()
        
        # Enter interactive mode
        print("\nEntering interactive mode...")
        system.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"System error: {e}")
    finally:
        system.stop_system()


if __name__ == "__main__":
    main()
