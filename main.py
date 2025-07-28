"""
Main entry point for the agentic system infrastructure (Docker container)
This runs only the core system components without interactive features
"""
import time
import signal
import sys
from core.logger import logger
from core.health_check import health_checker
from consumer.consumer_manager import consumer_manager


class AgenticSystemInfrastructure:
    """
    AgenticSystem infrastructure class for running in Docker containers.
    Only handles the core system components (agents, monitoring, Kafka).
    """
    
    def __init__(self):
        self.is_running = False
        
    def start_system(self):
        """
        Start the agentic system infrastructure only.

        

        Raises:
            Exception:
                An error occurred while starting the system.
        """
        try:
            logger.info("Starting Agentic Teaching System Infrastructure...")
            
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
            
            self.is_running = True
            logger.info("Agentic Teaching System Infrastructure started successfully!")
            
            # Show system status
            self._show_system_status()
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            self.stop_system()
            raise
    
    def stop_system(self):
        """
        Stop the agentic system infrastructure.

        
        """
        if not self.is_running:
            return
            
        logger.info("Stopping Agentic Teaching System...")
        
        # Stop consumers
        consumer_manager.stop_all_consumers()
        
        # Stop health monitoring
        health_checker.stop_monitoring()
        
        self.is_running = False
        logger.info("Agentic Teaching System stopped")
    
    def _show_system_status(self):
        """
        Show current system status.

        
        """
        print("\n" + "="*60)
        print("AGENTIC TEACHING SYSTEM INFRASTRUCTURE STATUS")
        print("="*60)
        
        # Health status
        health_status = health_checker.get_system_health()
        print(f"Kafka Status: {health_status['kafka']}")
        print(f"Registered Agents: {health_status['registered_agents']}")
        
        # Consumer status
        consumer_status = consumer_manager.get_consumer_status()
        print("\nActive Agents:")
        for agent_uuid, status in consumer_status.items():
            running_status = "🟢 Running" if status['is_running'] else "🔴 Stopped"
            print(f"  - {status['agent_type']}: {running_status} (Messages: {status['message_count']})")
        
        print("\n📡 Infrastructure Status: READY")
        print("🔗 External clients can now connect via Kafka")
        print("🐳 Running in Docker container mode")
        print("="*60)
    
    def keep_alive(self):
        """
        Keep the system running and responsive to shutdown signals.

        
        """
        logger.info("Infrastructure is running. Waiting for shutdown signal...")
        print("Infrastructure is now running. Press Ctrl+C to stop.")
        
        try:
            while self.is_running:
                time.sleep(5)
                # Optional: Periodic health check
                if not health_checker.get_system_health().get('kafka', False):
                    logger.warning("Kafka connection lost, attempting restart...")
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop_system()


def signal_handler(signum, frame):
    """
    Handle shutdown signals.

    Args:
        signum: Signal number.
        frame: Current stack frame.

    Returns:
        None
    """
    print("\nReceived shutdown signal. Stopping infrastructure...")
    if 'system' in globals():
        system.stop_system()
    sys.exit(0)


def main():
    """
    Main function for running infrastructure in Docker container.

    Returns:
        None

    Raises:
        KeyboardInterrupt:
            When system is interrupted by user.
        Exception:
            An error occurred during system execution.
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🐳 Starting Agentic Teaching System in Docker Infrastructure Mode")
    print("="*70)
    
    # Create and start system
    global system
    system = AgenticSystemInfrastructure()
    
    try:
        # Start the system infrastructure
        system.start_system()
        
        # Keep the system alive
        system.keep_alive()
        
    except KeyboardInterrupt:
        print("\nInfrastructure interrupted by user")
    except Exception as e:
        logger.error(f"Infrastructure error: {e}")
        print(f"Infrastructure error: {e}")
    finally:
        system.stop_system()
        print("Infrastructure shutdown complete.")


if __name__ == "__main__":
    main()
