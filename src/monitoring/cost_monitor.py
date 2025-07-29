"""
Cost monitoring system for tracking LLM usage and expenses with user-based tracking
"""

import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

from src.utils.logger import logger


@dataclass
class TokenUsageInfo:
    """
    TokenUsageInfo class containing token usage information from LLM engines.
    """
    timestamp: float
    request_id: str
    user_id: str
    agent_uuid: str
    agent_type: str
    model_name: str
    provider: str
    input_tokens: int
    output_tokens: int
    response_time: float
    success: bool
    error_message: str = ""


@dataclass
class RequestCostInfo:
    """
    RequestCostInfo class containing complete cost information for a request.
    """
    timestamp: float
    request_id: str
    user_id: str
    agent_uuid: str
    agent_type: str
    producer_uuid: str
    model_name: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    response_time: float
    success: bool
    error_message: str = ""


class CostMonitor:
    """
    Centralized cost monitoring system that receives token usage data 
    from LLM engines and calculates costs.
    """

    def __init__(self):
        self.requests: List[RequestCostInfo] = []
        self.user_costs: Dict[str, Dict[str, float]] = {}  # user_id -> {total_cost, daily_cost, etc.}
        self.lock = threading.Lock()
        self._kafka_consumer_started = False

    def start_token_usage_consumer(self):
        """Start Kafka consumer for receiving token usage data from LLM engines."""
        if self._kafka_consumer_started:
            logger.warning("Token usage consumer already started")
            return
            
        try:
            # Start background thread to consume token usage messages
            self.token_consumer_thread = threading.Thread(
                target=self._consume_token_usage_messages, 
                daemon=True
            )
            self.token_consumer_thread.start()
            self._kafka_consumer_started = True
            logger.info("Cost monitor token usage consumer started")
        except Exception as e:
            logger.error(f"Failed to setup token usage consumer: {e}")

    def _consume_token_usage_messages(self):
        """Background thread to consume token usage messages from LLM engines."""
        try:
            from src.messaging.kafka_client import kafka_client
            import src.config.settings as settings
            
            # Create consumer for token usage topic
            consumer = kafka_client.get_consumer(
                [settings.TOPIC_TOKEN_USAGE], 
                group_id="cost_monitor_group"
            )
            
            logger.info("Cost monitor listening for token usage messages...")
            
            while True:
                try:
                    message_pack = consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, messages in message_pack.items():
                        for message in messages:
                            self._process_token_usage_message(message.value)
                            
                except Exception as e:
                    logger.error(f"Error processing token usage message: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Token usage consumer error: {e}")

    def _process_token_usage_message(self, message: Dict):
        """Process token usage message from LLM engine and calculate costs."""
        try:
            token_usage = TokenUsageInfo(**message)
            
            # Calculate costs using cost calculator
            from src.utils.cost_calculator import cost_calculator
            
            cost_info = cost_calculator.calculate_request_cost(
                provider=token_usage.provider,
                input_tokens=token_usage.input_tokens,
                output_tokens=token_usage.output_tokens
            )
            
            # Create complete cost record
            cost_record = RequestCostInfo(
                timestamp=token_usage.timestamp,
                request_id=token_usage.request_id,
                user_id=token_usage.user_id,
                agent_uuid=token_usage.agent_uuid,
                agent_type=token_usage.agent_type,
                producer_uuid="",  # Will be filled by agent if needed
                model_name=token_usage.model_name,
                provider=token_usage.provider,
                input_tokens=token_usage.input_tokens,
                output_tokens=token_usage.output_tokens,
                total_tokens=token_usage.input_tokens + token_usage.output_tokens,
                input_cost=cost_info["input_cost"],
                output_cost=cost_info["output_cost"],
                total_cost=cost_info["total_cost"],
                response_time=token_usage.response_time,
                success=token_usage.success,
                error_message=token_usage.error_message
            )
            
            # Store the cost record
            self._store_cost_record(cost_record)
            
            logger.debug(f"Processed token usage for user {token_usage.user_id}: "
                        f"${cost_info['total_cost']:.6f}")
            
        except Exception as e:
            logger.error(f"Error processing token usage message: {e}")

    def _store_cost_record(self, cost_record: RequestCostInfo):
        """Store cost record and update user cost tracking."""
        with self.lock:
            # Add to requests list
            self.requests.append(cost_record)
            
            # Update user cost tracking
            user_id = cost_record.user_id
            if user_id not in self.user_costs:
                self.user_costs[user_id] = {
                    "total_cost": 0.0,
                    "daily_cost": 0.0,
                    "monthly_cost": 0.0,
                    "request_count": 0,
                    "last_request": 0.0
                }
            
            self.user_costs[user_id]["total_cost"] += cost_record.total_cost
            self.user_costs[user_id]["request_count"] += 1
            self.user_costs[user_id]["last_request"] = cost_record.timestamp
            
            # Update daily/monthly costs (simplified - you might want more sophisticated time window tracking)
            current_time = time.time()
            if current_time - cost_record.timestamp < 86400:  # 24 hours
                self.user_costs[user_id]["daily_cost"] += cost_record.total_cost
            if current_time - cost_record.timestamp < 2592000:  # 30 days
                self.user_costs[user_id]["monthly_cost"] += cost_record.total_cost

    def get_user_costs(self, user_id: str) -> Dict[str, Any]:
        """
        Get cost information for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user's cost information
        """
        with self.lock:
            if user_id not in self.user_costs:
                return {
                    "user_id": user_id,
                    "total_cost": 0.0,
                    "daily_cost": 0.0,
                    "monthly_cost": 0.0,
                    "request_count": 0,
                    "last_request": 0.0
                }
            
            return {
                "user_id": user_id,
                **self.user_costs[user_id]
            }

    def get_all_user_costs(self) -> Dict[str, Dict[str, Any]]:
        """Get cost information for all users."""
        with self.lock:
            return {
                user_id: {
                    "user_id": user_id,
                    **costs
                }
                for user_id, costs in self.user_costs.items()
            }

    def log_request(
        self,
        agent_uuid: str,
        agent_type: str,
        request_id: str,
        producer_uuid: str,
        cost_info: Dict[str, Any],
        response_time: float,
        model_name: str,
        success: bool,
        error_message: str = "",
        user_id: str = "anonymous"  # Add user_id parameter with default
    ):
        """
        Legacy method for backward compatibility. 
        Records cost information directly (for agents that haven't migrated to new system).
        
        Args:
            agent_uuid: Agent UUID
            agent_type: Agent type
            request_id: Request ID
            producer_uuid: Producer UUID (can be used as user_id if needed)
            cost_info: Cost information dictionary
            response_time: Response time in seconds
            model_name: Model name
            success: Whether request was successful
            error_message: Error message if any
            user_id: User identifier (defaults to "anonymous", can use producer_uuid if available)
        """
        try:
            # Use producer_uuid as user_id if user_id is default and producer_uuid is available
            effective_user_id = user_id if user_id != "anonymous" else (producer_uuid or "anonymous")
            
            # Extract cost information
            input_tokens = cost_info.get("input_tokens", 0)
            output_tokens = cost_info.get("output_tokens", 0)
            input_cost = cost_info.get("input_cost", 0.0)
            output_cost = cost_info.get("output_cost", 0.0)
            total_cost = cost_info.get("total_cost", 0.0)

            # Create cost record
            cost_record = RequestCostInfo(
                timestamp=time.time(),
                request_id=request_id,
                user_id=effective_user_id,
                agent_uuid=agent_uuid,
                agent_type=agent_type,
                producer_uuid=producer_uuid,
                model_name=model_name,
                provider=self._infer_provider_from_model(model_name),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                input_cost=input_cost,
                output_cost=output_cost,
                total_cost=total_cost,
                response_time=response_time,
                success=success,
                error_message=error_message
            )

            # Store the cost record
            self._store_cost_record(cost_record)

            logger.info(f"Cost logged for request {request_id}: ${total_cost:.6f} (user: {effective_user_id})")

        except Exception as e:
            logger.error(f"Failed to log cost for request {request_id}: {e}")

    def _infer_provider_from_model(self, model_name: str) -> str:
        """Infer provider from model name."""
        model_lower = model_name.lower()
        if "gemini" in model_lower:
            return "gemini"
        elif "llama" in model_lower or "ollama" in model_lower:
            return "ollama"
        elif "gpt" in model_lower or "openai" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "claude"
        else:
            return "unknown"

    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get cost statistics for specified time period

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with comprehensive statistics
        """
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_requests = [r for r in self.requests if r.timestamp >= cutoff_time]

            if not recent_requests:
                return {
                    "period_hours": hours,
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "average_cost_per_request": 0.0,
                    "average_tokens_per_request": 0.0,
                    "average_response_time": 0.0,
                    "by_agent_type": {},
                    "by_model": {},
                    "cost_trend": [],
                }

            # Basic statistics
            total_requests = len(recent_requests)
            successful_requests = sum(1 for r in recent_requests if r.success)
            failed_requests = total_requests - successful_requests
            total_cost = sum(r.total_cost for r in recent_requests)
            total_tokens = sum(r.total_tokens for r in recent_requests)
            average_response_time = (
                sum(r.response_time for r in recent_requests) / total_requests
            )

            # Statistics by agent type
            by_agent_type = {}
            for request in recent_requests:
                if request.agent_type not in by_agent_type:
                    by_agent_type[request.agent_type] = {
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                        "average_response_time": 0.0,
                    }

                stats = by_agent_type[request.agent_type]
                stats["requests"] += 1
                stats["cost"] += request.total_cost
                stats["tokens"] += request.total_tokens
                stats["average_response_time"] += request.response_time

            # Calculate averages for agent types
            for agent_type, stats in by_agent_type.items():
                if stats["requests"] > 0:
                    stats["average_response_time"] /= stats["requests"]
                    stats["average_cost_per_request"] = (
                        stats["cost"] / stats["requests"]
                    )
                    stats["average_tokens_per_request"] = (
                        stats["tokens"] / stats["requests"]
                    )

            # Statistics by model
            by_model = {}
            for request in recent_requests:
                if request.model_name not in by_model:
                    by_model[request.model_name] = {
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                    }

                by_model[request.model_name]["requests"] += 1
                by_model[request.model_name]["cost"] += request.total_cost
                by_model[request.model_name]["tokens"] += request.total_tokens

            # Cost trend (hourly breakdown)
            cost_trend = self._calculate_cost_trend(recent_requests, hours)

            return {
                "period_hours": hours,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / total_requests
                if total_requests > 0
                else 0,
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "average_cost_per_request": total_cost / total_requests
                if total_requests > 0
                else 0,
                "average_tokens_per_request": total_tokens / total_requests
                if total_requests > 0
                else 0,
                "average_response_time": average_response_time,
                "by_agent_type": by_agent_type,
                "by_model": by_model,
                "cost_trend": cost_trend,
            }

    def _calculate_cost_trend(
        self, requests: List[RequestCostInfo], hours: int
    ) -> List[Dict[str, Any]]:
        """
        Calculate hourly cost trend

        Args:
            requests: List of requests to analyze
            hours: Number of hours to analyze

        Returns:
            List of hourly cost data
        """
        if not requests:
            return []

        # Group requests by hour
        hourly_data = {}

        for request in requests:
            # Round timestamp to hour
            hour_timestamp = int(request.timestamp // 3600) * 3600

            if hour_timestamp not in hourly_data:
                hourly_data[hour_timestamp] = {
                    "timestamp": hour_timestamp,
                    "hour": datetime.fromtimestamp(hour_timestamp).strftime(
                        "%Y-%m-%d %H:00"
                    ),
                    "requests": 0,
                    "cost": 0.0,
                    "tokens": 0,
                }

            hourly_data[hour_timestamp]["requests"] += 1
            hourly_data[hour_timestamp]["cost"] += request.total_cost
            hourly_data[hour_timestamp]["tokens"] += request.total_tokens

        # Sort by timestamp
        trend = sorted(hourly_data.values(), key=lambda x: x["timestamp"])
        return trend

    def get_top_consumers(
        self, limit: int = 10, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get top cost consumers (by user_id)

        Args:
            limit: Maximum number of results
            hours: Hours to look back

        Returns:
            List of top consumers with their usage
        """
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_requests = [r for r in self.requests if r.timestamp >= cutoff_time]

            # Group by user_id
            consumers = {}
            for request in recent_requests:
                user_id = request.user_id
                if user_id not in consumers:
                    consumers[user_id] = {
                        "user_id": user_id,
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                        "agents_used": set(),
                    }

                consumer = consumers[user_id]
                consumer["requests"] += 1
                consumer["cost"] += request.total_cost
                consumer["tokens"] += request.total_tokens
                consumer["agents_used"].add(request.agent_type)

            # Convert sets to lists and sort by cost
            for consumer in consumers.values():
                consumer["agents_used"] = list(consumer["agents_used"])

            top_consumers = sorted(
                consumers.values(), key=lambda x: x["cost"], reverse=True
            )
            return top_consumers[:limit]

    def export_data(self, filename: str = None, hours: int = 24):
        """
        Export cost data to JSON file

        Args:
            filename: Output filename
            hours: Hours of data to export
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cost_data_{timestamp}.json"

        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_requests = [r for r in self.requests if r.timestamp >= cutoff_time]

            # Convert to serializable format
            export_data = {
                "export_timestamp": time.time(),
                "export_period_hours": hours,
                "total_requests": len(recent_requests),
                "requests": [asdict(r) for r in recent_requests],
                "statistics": self.get_statistics(hours),
                "user_costs": self.get_all_user_costs()
            }

            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Cost data exported to {filename}")
            except Exception as e:
                logger.error(f"Failed to export cost data: {e}")

    def cleanup_old_data(self, days: int = 30):
        """
        Remove data older than specified days

        Args:
            days: Number of days to keep
        """
        with self.lock:
            cutoff_time = time.time() - (days * 24 * 3600)
            old_count = len(self.requests)
            self.requests = [r for r in self.requests if r.timestamp >= cutoff_time]
            removed_count = old_count - len(self.requests)

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old cost records")


# Global cost monitor instance
cost_monitor = CostMonitor()
