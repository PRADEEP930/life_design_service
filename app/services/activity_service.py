from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.repository.activity_repository import InMemoryActivityRepository, get_activity_repository
from app.models.activity import Activity

class ActivityService:
    """Service layer for activity business logic"""
    
    def __init__(self, repository: InMemoryActivityRepository = None):
        self.repository = repository or get_activity_repository()
    
    def create_activity(self, activity_data: dict) -> Activity:
        """Create a new activity"""
        # Ensure timestamp
        if 'timestamp' not in activity_data:
            activity_data['timestamp'] = datetime.now().isoformat()
        
        return self.repository.add(activity_data)
    
    def get_goal_summary(self, goal_id: int) -> Dict[str, Any]:
        """Get summary for a specific goal"""
        activities = self.repository.get_by_goal(goal_id)
        
        if not activities:
            return {
                "total_activities": 0,
                "total_value": 0,
                "average_value": 0,
                "activity_by_type": {}
            }
        
        # Calculate totals
        total_value = sum(a.value for a in activities)
        
        # Group by type
        activity_by_type = {}
        for activity in activities:
            activity_type = activity.activity_type
            if activity_type not in activity_by_type:
                activity_by_type[activity_type] = {
                    "count": 0,
                    "total_value": 0
                }
            activity_by_type[activity_type]["count"] += 1
            activity_by_type[activity_type]["total_value"] += activity.value
        
        # Get last activity
        last_activity = max(activities, 
                           key=lambda a: a.timestamp)
        
        return {
            "total_activities": len(activities),
            "total_value": total_value,
            "average_value": total_value / len(activities),
            "activity_by_type": activity_by_type,
            "last_activity": last_activity.timestamp
        }
    
    def calculate_consistency_score(self, goal_id: int) -> float:
        """Calculate consistency score (0.0-1.0)"""
        activities = self.repository.get_by_goal(goal_id)
        
        if not activities:
            return 0.0
        
        # Get unique dates
        dates = sorted(set(datetime.fromisoformat(a.timestamp).date() 
                          for a in activities))
        
        if len(dates) < 2:
            return 0.5
        
        # Calculate longest streak
        max_streak = 0
        current_streak = 1
        
        for i in range(1, len(dates)):
            days_diff = (dates[i] - dates[i-1]).days
            if days_diff == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        score = max_streak / len(dates)
        return round(min(score, 1.0), 2)