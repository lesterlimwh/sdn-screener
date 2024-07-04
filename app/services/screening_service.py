"""
This module provides methods for the screening service
"""

from typing import Dict, List, Tuple
from app.schemas import Person, PersonScreeningResult
from app.database import MongoDB
from app.utils.redis_utils import RedisUtil


class ScreeningService:
    def __init__(self, people: List[Person]):
        self.db_client = MongoDB()
        self.people = people
        self.person_map = self.__get_person_map()
        self.redis_util = RedisUtil()

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
    async def _store_screening_results(
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

        if operations:
            await self.db_client.bulk_upsert_documents('person', operations)

    async def _get_recently_screened_people(
        self
    ) -> Tuple[List[Person], List[PersonScreeningResult]]:
        """
        Find the people who were not recently screened and
        the results of recent screenings

        Returns:
            A list of people who were not recently screened
            A list of results from recent screenings
        """
        cache_misses = []
        cache_person_screening_results = []

        for person in self.people:
            key = f'{person.name}-{person.dob}-{person.country}'
            cached_data = await self.redis_util.get_dict(key)
            if cached_data:
                cached_data['id'] = person.id
                cache_person_screening_results.append(cached_data)
                continue
            cache_misses.append(person)

        return cache_misses, cache_person_screening_results

    async def _update_screening_results_cache(
        self,
        person_screening_results: List[PersonScreeningResult]
    ) -> None:
        """
        Update the cache with fresh screening results

        Args:
            person_screening_results: A list of screening results for each person
        """
        for screening_result in person_screening_results:
            person_id = int(screening_result['id'])
            name = self.person_map[person_id]['name']
            dob = self.person_map[person_id]['dob']
            country = self.person_map[person_id]['country']

            # construct the redis cache key and store the screening result
            key = f'{name}-{dob}-{country}'
            await self.redis_util.set_dict(key, screening_result)

    # Public methods
    async def get_screening_results(self) -> List[PersonScreeningResult]:
        """
        Obtain the screening results for each person

        Args:
            people: A list of Person objects

        Returns:
            A list of screening results for each person
        """
        raise NotImplementedError("Subclasses must implement this method")
