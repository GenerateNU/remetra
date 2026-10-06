"""Service layer for meal follow up business logic."""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone 

from repositories.food_log_repository import FoodLogRepository

class MealFollowUpsService:
    """Service for meal follow ups business logic."""

    def __init__(self):
        self.food_log_repo = FoodLogRepository()

    def should_schedule(self, food_log_id:UUID, now=datetime.now(timezone.utc)):
        """Compare food log timestamp with current time"""
        food_log = self.food_log_repo.get_food_log_by_id(food_log_id) 
        seconds_difference = now - food_log.timestamp 
        hours_diffference = seconds_difference.total_seconds() / 3600
        if hours_diffference < 2: # within 2 hour window
            return True
        return False 
    
    
    
    

    






