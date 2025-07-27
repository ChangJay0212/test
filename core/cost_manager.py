"""
Cost monitoring management interface
"""
import time
from typing import Dict, Any, List
from core.cost_monitor import cost_monitor
from core.logger import logger
from core.health_check import health_checker


class CostMonitorManager:
    """
    Manager for cost monitoring operations and reporting
    """
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for cost monitoring
        
        Returns:
            Dictionary with dashboard information
        """
        try:
            # Get statistics for different time periods
            hourly_stats = cost_monitor.get_statistics(hours=1)
            daily_stats = cost_monitor.get_statistics(hours=24)
            weekly_stats = cost_monitor.get_statistics(hours=168)  # 7 days
            
            # Get top consumers
            top_consumers = cost_monitor.get_top_consumers(limit=10, hours=24)
            
            # Get system health
            system_health = health_checker.get_system_health()
            
            # Calculate uptime
            uptime_seconds = time.time() - self.start_time
            uptime_hours = uptime_seconds / 3600
            
            return {
                "system_info": {
                    "uptime_hours": uptime_hours,
                    "health_status": system_health,
                    "monitoring_since": self.start_time
                },
                "cost_overview": {
                    "last_hour": {
                        "requests": hourly_stats["total_requests"],
                        "cost": hourly_stats["total_cost"],
                        "tokens": hourly_stats["total_tokens"],
                        "success_rate": hourly_stats["success_rate"]
                    },
                    "last_24_hours": {
                        "requests": daily_stats["total_requests"],
                        "cost": daily_stats["total_cost"],
                        "tokens": daily_stats["total_tokens"],
                        "success_rate": daily_stats["success_rate"]
                    },
                    "last_week": {
                        "requests": weekly_stats["total_requests"],
                        "cost": weekly_stats["total_cost"],
                        "tokens": weekly_stats["total_tokens"],
                        "success_rate": weekly_stats["success_rate"]
                    }
                },
                "agent_performance": daily_stats["by_agent_type"],
                "model_usage": daily_stats["by_model"],
                "cost_trend": daily_stats["cost_trend"],
                "top_consumers": top_consumers,
                "alerts": self._generate_alerts(daily_stats)
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {"error": str(e)}
    
    def _generate_alerts(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate cost and usage alerts
        
        Args:
            stats: Statistics data
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # High cost alert
        if stats["total_cost"] > 10.0:  # More than $10 in 24 hours
            alerts.append({
                "type": "high_cost",
                "level": "warning",
                "message": f"High daily cost: ${stats['total_cost']:.2f}",
                "details": f"Total cost in last 24 hours exceeds $10"
            })
        
        # High failure rate alert
        if stats["success_rate"] < 0.9 and stats["total_requests"] > 10:
            alerts.append({
                "type": "high_failure_rate",
                "level": "error", 
                "message": f"High failure rate: {(1-stats['success_rate'])*100:.1f}%",
                "details": f"Success rate below 90% with {stats['failed_requests']} failures"
            })
        
        # High average response time alert
        if stats["average_response_time"] > 10.0:  # More than 10 seconds
            alerts.append({
                "type": "slow_response",
                "level": "warning",
                "message": f"Slow average response time: {stats['average_response_time']:.1f}s",
                "details": "Consider optimizing prompts or checking API performance"
            })
        
        # No requests alert
        if stats["total_requests"] == 0:
            alerts.append({
                "type": "no_activity",
                "level": "info",
                "message": "No requests in the last 24 hours",
                "details": "System is idle"
            })
        
        return alerts
    
    def get_cost_report(self, format: str = "summary") -> str:
        """
        Generate a cost report in different formats
        
        Args:
            format: Report format ('summary', 'detailed', 'csv')
            
        Returns:
            Formatted report string
        """
        try:
            stats = cost_monitor.get_statistics(hours=24)
            
            if format == "summary":
                return self._generate_summary_report(stats)
            elif format == "detailed":
                return self._generate_detailed_report(stats)
            elif format == "csv":
                return self._generate_csv_report(stats)
            else:
                return "Invalid format. Use 'summary', 'detailed', or 'csv'"
                
        except Exception as e:
            logger.error(f"Error generating cost report: {e}")
            return f"Error generating report: {str(e)}"
    
    def _generate_summary_report(self, stats: Dict[str, Any]) -> str:
        """Generate summary cost report"""
        report = f"""
=== COST MONITORING SUMMARY (Last 24 Hours) ===

📊 Overall Statistics:
• Total Requests: {stats['total_requests']}
• Successful Requests: {stats['successful_requests']}
• Failed Requests: {stats['failed_requests']} 
• Success Rate: {stats['success_rate']*100:.1f}%

💰 Cost Breakdown:
• Total Cost: ${stats['total_cost']:.6f}
• Average Cost per Request: ${stats['average_cost_per_request']:.6f}
• Total Tokens Used: {stats['total_tokens']:,}
• Average Tokens per Request: {stats['average_tokens_per_request']:.0f}

⏱️ Performance:
• Average Response Time: {stats['average_response_time']:.2f} seconds

🤖 By Agent Type:
"""
        
        for agent_type, agent_stats in stats['by_agent_type'].items():
            report += f"• {agent_type.title().replace('_', ' ')}: "
            report += f"{agent_stats['requests']} requests, "
            report += f"${agent_stats['cost']:.6f}, "
            report += f"{agent_stats['tokens']:,} tokens\n"
        
        report += f"\n🔧 By Model:\n"
        for model, model_stats in stats['by_model'].items():
            report += f"• {model}: "
            report += f"{model_stats['requests']} requests, "
            report += f"${model_stats['cost']:.6f}\n"
        
        return report
    
    def _generate_detailed_report(self, stats: Dict[str, Any]) -> str:
        """Generate detailed cost report"""
        report = self._generate_summary_report(stats)
        
        report += f"\n📈 Hourly Cost Trend:\n"
        for hour_data in stats['cost_trend']:
            report += f"• {hour_data['hour']}: "
            report += f"{hour_data['requests']} requests, "
            report += f"${hour_data['cost']:.6f}, "
            report += f"{hour_data['tokens']:,} tokens\n"
        
        # Get top consumers
        top_consumers = cost_monitor.get_top_consumers(limit=5, hours=24)
        if top_consumers:
            report += f"\n👥 Top 5 Consumers:\n"
            for i, consumer in enumerate(top_consumers, 1):
                report += f"{i}. Producer {consumer['producer_uuid'][:8]}...: "
                report += f"{consumer['requests']} requests, "
                report += f"${consumer['cost']:.6f}, "
                report += f"Agents used: {', '.join(consumer['agents_used'])}\n"
        
        return report
    
    def _generate_csv_report(self, stats: Dict[str, Any]) -> str:
        """Generate CSV format cost report"""
        csv_lines = [
            "Metric,Value,Unit",
            f"Total Requests,{stats['total_requests']},count",
            f"Successful Requests,{stats['successful_requests']},count",
            f"Failed Requests,{stats['failed_requests']},count",
            f"Success Rate,{stats['success_rate']*100:.2f},%",
            f"Total Cost,{stats['total_cost']:.6f},USD",
            f"Average Cost per Request,{stats['average_cost_per_request']:.6f},USD",
            f"Total Tokens,{stats['total_tokens']},count",
            f"Average Tokens per Request,{stats['average_tokens_per_request']:.0f},count",
            f"Average Response Time,{stats['average_response_time']:.2f},seconds"
        ]
        
        return "\n".join(csv_lines)
    
    def get_budget_alert(self, daily_budget: float) -> Dict[str, Any]:
        """
        Check if current usage is within budget
        
        Args:
            daily_budget: Daily budget limit in USD
            
        Returns:
            Budget status information
        """
        try:
            stats = cost_monitor.get_statistics(hours=24)
            current_cost = stats["total_cost"]
            
            percentage_used = (current_cost / daily_budget) * 100 if daily_budget > 0 else 0
            
            if percentage_used >= 100:
                status = "over_budget"
                level = "error"
            elif percentage_used >= 80:
                status = "near_budget"
                level = "warning"
            elif percentage_used >= 50:
                status = "moderate_usage"
                level = "info"
            else:
                status = "within_budget"
                level = "success"
            
            return {
                "status": status,
                "level": level,
                "daily_budget": daily_budget,
                "current_cost": current_cost,
                "remaining_budget": max(0, daily_budget - current_cost),
                "percentage_used": percentage_used,
                "message": f"Used ${current_cost:.6f} of ${daily_budget:.2f} budget ({percentage_used:.1f}%)"
            }
            
        except Exception as e:
            logger.error(f"Error checking budget: {e}")
            return {"error": str(e)}
    
    def export_data(self, hours: int = 24) -> str:
        """
        Export cost data to file
        
        Args:
            hours: Hours of data to export
            
        Returns:
            Filename of exported data
        """
        try:
            filename = f"cost_export_{int(time.time())}.json"
            cost_monitor.export_data(filename, hours)
            return filename
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return f"Error: {str(e)}"


# Global cost monitor manager instance
cost_monitor_manager = CostMonitorManager()
