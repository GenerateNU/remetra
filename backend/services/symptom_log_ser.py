from models.symptom_log_model import SymptomLogCreate, SymptomLogResponse
from repositories.symptom_log_repo import SymptomLogRepository                       
                                                                                       

class SymptomLogService:
    """Business logic for symptom logs."""

    def __init__(self, repo: SymptomLogRepository):
        self.repo = repo

    async def get_symptom_log(self, log_id: int) -> SymptomLogResponse | None:
        return await self.repo.get_by_id(log_id)

    async def create_symptom_log(self, data: SymptomLogCreate) -> SymptomLogResponse:
        return await self.repo.create(data)

    async def delete_symptom_log(self, log_id: int) -> bool:
        return await self.repo.delete(log_id)