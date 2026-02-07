from datetime import datetime
from decimal import Decimal
from typing import Optional
import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field

class symptom_log(BaseModel):
    __tablename__ = 'symptom_logs'
    """
    Pydantic model for symptom log entries.
    """

    model_config = ConfigDict(from_attributes=True)  # Allows loading from database models (SQLAlchemy)

    log_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    symptom_id = sa.Column(sa.Integer, sa.ForeignKey('symptoms.symptom_id'), nullable=False)
    intensity = sa.Column(sa.Integer, nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    duration = sa.Column(sa.Integer, nullable=True)  

    

    
