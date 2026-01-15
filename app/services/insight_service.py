from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.repository.activity_repository import InMemoryActivityRepository, get_activity_repository

class InsightService:
    """Service layer for insight generation"""
    
    def __init__(self, repository: InMemoryActivityRepository = None):
        self.repository = repository or get_activity_repository()
    
    def get_weekly_health_total(self, goal_id: int) -> float:
        """Calculate weekly health activities total"""
        one_week_ago = datetime.now() - timedelta(days=7)
        activities = self.repository.get_by_goal(goal_id)
        
        health_total = 0
        for activity in activities:
            if activity.activity_type == "Health":
                activity_time = datetime.fromisoformat(activity.timestamp)
                if activity_time >= one_week_ago:
                    health_total += activity.value
        
        return health_total
    
    def generate_wellness_insights(self, goal_id: int) -> Dict[str, Any]:
        """Generate wellness-related insights"""
        activities = self.repository.get_by_goal(goal_id)
        
        # Calculate totals
        health_total = 0
        learning_total = 0
        
        for activity in activities:
            if activity.activity_type == "Health":
                health_total += activity.value
            elif activity.activity_type == "Learning":
                learning_total += activity.value
        
        weekly_health = self.get_weekly_health_total(goal_id)
        wellness_warning = weekly_health < 150
        
        # Generate recommendation
        recommendation = ""
        if weekly_health < 150:
            if learning_total > 300:
                recommendation = "High learning activity detected but physical wellness is low. Consider rebalancing your growth plan."
            else:
                recommendation = "Try to reach 150+ minutes of health activities per week for optimal wellness."
        elif learning_total > 400:
            recommendation = "Great learning consistency! Keep maintaining your study habits."
        else:
            recommendation = "Your activity pattern looks balanced. Keep tracking your progress!"
        
        return {
            "weekly_health_total": weekly_health,
            "wellness_warning": wellness_warning,
            "recommendation": recommendation,
            "learning_total": learning_total,
            "health_total": health_total
        }
    
    def get_productivity_recommendation(self, goal_id: int) -> Dict[str, Any]:
        """Generate productivity recommendations"""
        activities = self.repository.get_by_goal(goal_id)
        
        if not activities:
            return {
                "recommendations": ["Start logging activities to get personalized insights!"],
                "total_activities": 0
            }
        
        # Activity analysis
        activity_count = len(activities)
        activity_types = set(a.activity_type for a in activities)
        
        recommendations = []
        
        # Variety check
        if len(activity_types) < 2:
            recommendations.append("Try diversifying your activities across different types for holistic growth.")
        
        # Consistency encouragement
        if activity_count > 10:
            recommendations.append(f"Great consistency! You've logged {activity_count} activities.")
        
        # Health focus
        health_activities = [a for a in activities if a.activity_type == "Health"]
        if len(health_activities) < 3:
            recommendations.append("Consider adding more health activities to your routine.")
        
        return {
            "recommendations": recommendations or ["Keep up the good work! Continue tracking your progress."],
            "total_activities": activity_count,
            "activity_types": list(activity_types)
        }