"""
Cost monitoring system for tracking LLM usage and expenses
"""
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from core.logger import logger
import threading


@dataclass
class RequestCostInfo:
    """Information about a single request's cost"""
    timestamp: float
    agent_uuid: str
    agent_type: str
    request_id: str
    producer_uuid: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    response_time: float
    model_name: str
    success: bool
    error_message: str = ""


class CostMonitor:
    """
    Centralized cost monitoring system
    """
    
    def __init__(self):
        self.requests: List[RequestCostInfo] = []
        self.lock = threading.Lock()
        
    def log_request(self, 
                   agent_uuid: str,
                   agent_type: str, 
                   request_id: str,
                   producer_uuid: str,
                   cost_info: Dict[str, Any],
                   response_time: float,
                   model_name: str,
                   success: bool,
                   error_message: str = ""):
        """
        Log a request's cost information
        
        Args:
            agent_uuid: Agent that processed the request
            agent_type: Type of agent
            request_id: Unique request identifier
            producer_uuid: Student/producer identifier
            cost_info: Cost breakdown from LLM engine
            response_time: Time taken to process request
            model_name: LLM model used
            success: Whether request was successful
            error_message: Error message if failed
        """
        with self.lock:
            request_cost = RequestCostInfo(
                timestamp=time.time(),
                agent_uuid=agent_uuid,
                agent_type=agent_type,
                request_id=request_id,
                producer_uuid=producer_uuid,
                input_tokens=cost_info.get('input_tokens', 0),
                output_tokens=cost_info.get('output_tokens', 0),
                total_tokens=cost_info.get('input_tokens', 0) + cost_info.get('output_tokens', 0),
                input_cost=cost_info.get('input_cost', 0.0),
                output_cost=cost_info.get('output_cost', 0.0),
                total_cost=cost_info.get('total_cost', 0.0),
                response_time=response_time,
                model_name=model_name,
                success=success,
                error_message=error_message
            )
            
            self.requests.append(request_cost)
            
            # Log the cost information
            logger.info(f"Cost logged: {agent_type} request ${request_cost.total_cost:.6f}, "
                       f"tokens: {request_cost.total_tokens}, time: {response_time:.2f}s")
    
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
                    "cost_trend": []
                }
            
            # Basic statistics
            total_requests = len(recent_requests)
            successful_requests = sum(1 for r in recent_requests if r.success)
            failed_requests = total_requests - successful_requests
            total_cost = sum(r.total_cost for r in recent_requests)
            total_tokens = sum(r.total_tokens for r in recent_requests)
            average_response_time = sum(r.response_time for r in recent_requests) / total_requests
            
            # Statistics by agent type
            by_agent_type = {}
            for request in recent_requests:
                if request.agent_type not in by_agent_type:
                    by_agent_type[request.agent_type] = {
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                        "average_response_time": 0.0
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
                    stats["average_cost_per_request"] = stats["cost"] / stats["requests"]
                    stats["average_tokens_per_request"] = stats["tokens"] / stats["requests"]
            
            # Statistics by model
            by_model = {}
            for request in recent_requests:
                if request.model_name not in by_model:
                    by_model[request.model_name] = {
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0
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
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
                "average_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
                "average_response_time": average_response_time,
                "by_agent_type": by_agent_type,
                "by_model": by_model,
                "cost_trend": cost_trend
            }
    
    def _calculate_cost_trend(self, requests: List[RequestCostInfo], hours: int) -> List[Dict[str, Any]]:
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
        current_time = time.time()
        
        for request in requests:
            # Round timestamp to hour
            hour_timestamp = int(request.timestamp // 3600) * 3600
            
            if hour_timestamp not in hourly_data:
                hourly_data[hour_timestamp] = {
                    "timestamp": hour_timestamp,
                    "hour": datetime.fromtimestamp(hour_timestamp).strftime("%Y-%m-%d %H:00"),
                    "requests": 0,
                    "cost": 0.0,
                    "tokens": 0
                }
            
            hourly_data[hour_timestamp]["requests"] += 1
            hourly_data[hour_timestamp]["cost"] += request.total_cost
            hourly_data[hour_timestamp]["tokens"] += request.total_tokens
        
        # Sort by timestamp
        trend = sorted(hourly_data.values(), key=lambda x: x["timestamp"])
        return trend
    
    def get_top_consumers(self, limit: int = 10, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get top cost consumers (by producer/student)
        
        Args:
            limit: Maximum number of results
            hours: Hours to look back
            
        Returns:
            List of top consumers with their usage
        """
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_requests = [r for r in self.requests if r.timestamp >= cutoff_time]
            
            # Group by producer
            consumers = {}
            for request in recent_requests:
                if request.producer_uuid not in consumers:
                    consumers[request.producer_uuid] = {
                        "producer_uuid": request.producer_uuid,
                        "requests": 0,
                        "cost": 0.0,
                        "tokens": 0,
                        "agents_used": set()
                    }
                
                consumer = consumers[request.producer_uuid]
                consumer["requests"] += 1
                consumer["cost"] += request.total_cost
                consumer["tokens"] += request.total_tokens
                consumer["agents_used"].add(request.agent_type)
            
            # Convert sets to lists and sort by cost
            for consumer in consumers.values():
                consumer["agents_used"] = list(consumer["agents_used"])
            
            top_consumers = sorted(consumers.values(), key=lambda x: x["cost"], reverse=True)
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
                "statistics": self.get_statistics(hours)
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
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
