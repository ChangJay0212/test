"""
Cost monitoring API for querying user costs and system statistics
"""

from typing import Dict, Any, List
from src.monitoring.cost_monitor import cost_monitor
from src.utils.logger import logger


class CostAPI:
    """
    API interface for cost monitoring and user cost queries.
    """

    @staticmethod
    def get_user_cost(user_id: str) -> Dict[str, Any]:
        """
        Get cost information for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user's cost information
        """
        try:
            return cost_monitor.get_user_costs(user_id)
        except Exception as e:
            logger.error(f"Error getting user cost for {user_id}: {e}")
            return {
                "user_id": user_id,
                "total_cost": 0.0,
                "daily_cost": 0.0,
                "monthly_cost": 0.0,
                "request_count": 0,
                "last_request": 0.0,
                "error": str(e)
            }

    @staticmethod
    def get_all_user_costs() -> Dict[str, Dict[str, Any]]:
        """
        Get cost information for all users.
        
        Returns:
            Dictionary with all users' cost information
        """
        try:
            return cost_monitor.get_all_user_costs()
        except Exception as e:
            logger.error(f"Error getting all user costs: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_top_consumers(limit: int = 10, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get top cost consumers.
        
        Args:
            limit: Maximum number of results
            hours: Hours to look back
            
        Returns:
            List of top consumers
        """
        try:
            return cost_monitor.get_top_consumers(limit=limit, hours=hours)
        except Exception as e:
            logger.error(f"Error getting top consumers: {e}")
            return []

    @staticmethod
    def get_cost_statistics(hours: int = 24) -> Dict[str, Any]:
        """
        Get cost statistics for specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with cost statistics
        """
        try:
            return cost_monitor.get_statistics(hours=hours)
        except Exception as e:
            logger.error(f"Error getting cost statistics: {e}")
            return {
                "period_hours": hours,
                "total_requests": 0,
                "total_cost": 0.0,
                "error": str(e)
            }

    @staticmethod
    def export_user_costs(filename: str = None, hours: int = 24) -> str:
        """
        Export cost data to file.
        
        Args:
            filename: Output filename
            hours: Hours of data to export
            
        Returns:
            Status message
        """
        try:
            cost_monitor.export_data(filename=filename, hours=hours)
            return f"Cost data exported successfully to {filename or 'auto-generated filename'}"
        except Exception as e:
            logger.error(f"Error exporting cost data: {e}")
            return f"Error exporting cost data: {e}"

    @staticmethod
    def get_user_cost_summary() -> Dict[str, Any]:
        """
        Get a summary of user costs with basic statistics.
        
        Returns:
            Dictionary with user cost summary
        """
        try:
            all_users = cost_monitor.get_all_user_costs()
            
            if not all_users:
                return {
                    "total_users": 0,
                    "total_system_cost": 0.0,
                    "average_cost_per_user": 0.0,
                    "users": []
                }
            
            total_cost = sum(user["total_cost"] for user in all_users.values())
            average_cost = total_cost / len(all_users) if all_users else 0.0
            
            # Sort users by total cost
            sorted_users = sorted(
                all_users.values(), 
                key=lambda x: x["total_cost"], 
                reverse=True
            )
            
            return {
                "total_users": len(all_users),
                "total_system_cost": total_cost,
                "average_cost_per_user": average_cost,
                "highest_cost_user": sorted_users[0] if sorted_users else None,
                "users": sorted_users[:10]  # Top 10 users by cost
            }
            
        except Exception as e:
            logger.error(f"Error getting user cost summary: {e}")
            return {
                "total_users": 0,
                "total_system_cost": 0.0,
                "average_cost_per_user": 0.0,
                "error": str(e)
            }


# Global cost API instance
cost_api = CostAPI()
