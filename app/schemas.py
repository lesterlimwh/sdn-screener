"""
This module provides schemas for a person
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Person(BaseModel):
    """
    Schema of a person
    """
    id: Optional[int]
    name: str
    dob: datetime
    country: str


class PersonScreeningResult(BaseModel):
    """
    Schema for a person's screening result
    """
    id: Optional[int]
    name_match: bool
    dob_match: bool
    country_match: bool
