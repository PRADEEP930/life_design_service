from typing import List, Optional, Dict
from app.repository import BaseRepository  # Import from package
from app.models.activity import Activity

class InMemoryActivityRepository(BaseRepository):
    """In-memory implementation of activity repository"""
    
    def __init__(self):
        self._storage: Dict[int, Activity] = {}
        self._next_id = 1
        self._goal_index: Dict[int, List[int]] = {}
    
    def add(self, activity_data: dict) -> Activity:
        """Add a new activity"""
        activity = Activity(
            id=self._next_id,
            **activity_data
        )
        
        self._storage[self._next_id] = activity
        self._next_id += 1
        
        # Index by goal_id for fast queries
        if activity.goal_id not in self._goal_index:
            self._goal_index[activity.goal_id] = []
        self._goal_index[activity.goal_id].append(activity.id)
        
        return activity
    
    def get_by_id(self, activity_id: int) -> Optional[Activity]:
        """Get activity by ID"""
        return self._storage.get(activity_id)
    
    def get_by_goal(self, goal_id: int) -> List[Activity]:
        """Get all activities for a goal"""
        if goal_id not in self._goal_index:
            return []
        
        return [self._storage[activity_id] 
                for activity_id in self._goal_index[goal_id]
                if activity_id in self._storage]
    
    def get_all(self) -> List[Activity]:
        """Get all activities"""
        return list(self._storage.values())
    
    def get_by_type(self, activity_type: str) -> List[Activity]:
        """Get activities by type"""
        return [activity for activity in self._storage.values()
                if activity.activity_type == activity_type]

# Factory function for dependency injection
def get_activity_repository():
    return InMemoryActivityRepository()