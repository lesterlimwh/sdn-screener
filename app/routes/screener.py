from typing import List
from fastapi import APIRouter
from app.schemas import Person, PersonScreeningResult
from app.services.ofac_screening_service import OfacScreeningService


router = APIRouter()

@router.post('/screen/', response_model=List[PersonScreeningResult])
async def screening_results(people: List[Person]) -> List[PersonScreeningResult]:
    ofac_screening_service = OfacScreeningService(people)
    return await ofac_screening_service.get_screening_results()
