import uuid 
from typing import Optional 

from pydantic import BaseModel, ConfigDict, Field

class CreateChunk(BaseModel): 
    "Used to create the chunk"

class ChunkResponse(BaseModel):
    "retrieved chunk returned to the user"