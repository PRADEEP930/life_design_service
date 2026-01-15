from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Activity:
    """Activity data model"""
    id: int
    goal_id: int
    activity_type: str
    value: float
    timestamp: str
    notes: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        return cls(**data)