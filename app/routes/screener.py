from typing import List
from fastapi import APIRouter
from app.schemas import Person, PersonScreeningResult
from app.services.screening_service import ScreeningService


router = APIRouter()
screening_service = ScreeningService()

@router.post('/screen/', response_model=List[PersonScreeningResult])
def screen_person(people: List[Person]):
    return screening_service.get_screening_results(people)
