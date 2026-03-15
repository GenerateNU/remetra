""" 
This is where you will define the functions for getting the food/symptom
Log entry DTOsw from joining the food/symptom table with the food/symptom log table
"""
from sqlalchemy.orm import Session

from models import FoodLogEntry, SymptomLogEntry


async def fetch_food_logs(db: Session, username: str) -> list[FoodLogEntry]: 
  return

async def fetch_symptom_logs(db: Session, username: str) -> list[SymptomLogEntry]: 
  return
