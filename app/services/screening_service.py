"""
This module provides methods for the screening service
"""

from typing import Dict, List
from app.schemas import Person, PersonScreeningResult
from app.database import MongoDB


class ScreeningService:
    def __init__(self, people: List[Person]):
        self.db_client = MongoDB()
        self.people = people
        self.person_map = self.__get_person_map()

    # Private methods
    def __get_person_map(self) -> Dict[int, Dict[str, str]]:
        """
        Transforms a list of People into a dictionary where id is the key

        Args:
            people: A list of Person objects
        """
        person_map = {}
        for person in self.people:
            person_map[person.id] = {
                'name': person.name,
                'dob': person.dob,
                'country': person.country
            }
        return person_map

    # Protected methods
    def _store_screening_results(
        self,
        person_screening_results: List[PersonScreeningResult]
    ) -> None:
        """
        Stores a list of screening results into the database

        Args:
            people: A list of Person objects
            person_screening_results: A list of screening results for each person
        """
        # bulk upsert every person's data to the person collection
        operations = []
        for person_screening_result in person_screening_results:
            person_id = person_screening_result['id']

            # use the triple (name, dob, country) as the unique identifier
            filter_query = self.person_map[person_id]

            # combine the person's data with their screening results and store it
            # remove the ID as it is only used within the context of an instance
            update_values = {**filter_query, **person_screening_result}
            del update_values['id']

            operation = {
                'filter_query': filter_query,
                'update_values': update_values
            }
            operations.append(operation)

        self.db_client.bulk_upsert_documents('person', operations)

    # Public methods
    def get_screening_results(self) -> List[PersonScreeningResult]:
        """
        Obtain the screening results for each person

        Args:
            people: A list of Person objects

        Returns:
            A list of screening results for each person
        """
        raise NotImplementedError("Subclasses must implement this method")
