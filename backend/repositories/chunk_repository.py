import logging
from typing import List

from sqlalchemy.orm import Session

from models.knowledge_chunk import KnowledgeChunk


class ChunkRepository:
    """
    Repository for handling database interactions related to knowledge chunks.

    This is where all the actual database queries happen. Services call these methods
    to get data from the database, and then apply business logic on top of it.
    """

    def __init__(self):
        ## define db session here:
        self.largest_id = 0

    def get_top_chunks(self, db: Session, query: List[float], n: int) -> List[KnowledgeChunk]:
        """
        Retrieve best match chunks in the database

        Returns:
            best match chunks in the database
        """
        logging.info("Retrieving best match chunks from the database")

        distance = KnowledgeChunk.embedding.cosine_distance(query)
        return db.query(KnowledgeChunk).order_by(distance).limit(n).all()
