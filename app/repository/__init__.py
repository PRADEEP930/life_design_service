 # Repository pattern interface

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.activity import Activity

class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    def add(self, activity_data: dict) -> Activity:
        pass
    
    @abstractmethod
    def get_by_id(self, activity_id: int) -> Optional[Activity]:
        pass
    
    @abstractmethod
    def get_by_goal(self, goal_id: int) -> List[Activity]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Activity]:
        pass

# Export BaseRepository from the package
__all__ = ['BaseRepository']