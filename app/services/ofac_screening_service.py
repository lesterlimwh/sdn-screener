"""
This module provides methods for the OFAC screening service
"""

import os
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv
from app.schemas import Person, PersonScreeningResult
from app.services.screening_service import ScreeningService


class OfacScreeningService(ScreeningService):
    # Set default timeout to 10 seconds
    OFAC_API_TIMEOUT = 10

    class OfacScreeningServiceError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    def __init__(self, people: List[Person]):
        # load the OFAC-related environment variables
        load_dotenv()
        self.ofac_api_key = os.getenv('OFAC_API_KEY')
        self.ofac_api_url = os.getenv('OFAC_API_URL')
        super().__init__(people)

    # Private methods
    def __update_name_and_dob_match(
        self,
        person_screening_result: PersonScreeningResult,
        match_fields: List[Optional[Dict[str, str]]]
    ) -> None:
        """
        Updates the name and dob match status in the person's screening result
        
        Args:
            person_screening_result: An object representing the screening result of this person
            match_fields: A list of dicts with the fieldName property
        """
        for match_field in match_fields:
            # prematurely exit the loop when both name and dob matches are already found
            if person_screening_result['name_match'] and person_screening_result['dob_match']:
                break

            field_name = match_field.get('fieldName')
            if field_name == 'Name':
                person_screening_result['name_match'] = True
                continue

            if field_name == "DOB":
                person_screening_result['dob_match'] = True

    def __update_country_match(
        self,
        person_screening_result: PersonScreeningResult,
        sanction: Dict[str, Any],
        country: str
    ) -> None:
        """
        Updates the country match status in the person's screening result
        
        Args:
            person_screening_result: An object representing the screening result of this person
            sanction: A dict that may contain the addresses and personDetails properties
            country: The country that belongs to this person
        """
        # look for country match in addresses
        addresses = sanction.get('addresses', [])
        for address in addresses:
            if address.get('country') == country:
                person_screening_result['country_match'] = True
                return

        # look for country match in citizenships
        person_details = sanction.get('personDetails', {})
        citizenships = person_details.get('citizenships', [])
        for citizenship in citizenships:
            if citizenship == country:
                person_screening_result['country_match'] = True
                return

        # look for country match in nationalities
        nationalities = person_details.get('nationalities', {})
        for nationality in nationalities:
            if nationality == country:
                person_screening_result['country_match'] = True
                return

    def __get_ofac_screening_response(self, people: List[Person]) -> Dict:
        """
        Makes a POST request to the OFAC API endpoint
        to obtain screening results for each person
        
        Args:
            people: A list of Person objects
        
        Returns:
            A dictionary response directly from OFAC API:
            https://docs.ofac-api.com/screening-api/response
        """
        # construct a case for each person
        cases = []
        for person in people:
            case = {
                'id': person.id,
                'name': person.name,
                'dob': person.dob.isoformat(),
                'citizenship': person.country,
                'nationality': person.country,
                'address': {
                    'country': person.country
                }
            }
            cases.append(case)

        # construct the headers and body of the request
        headers = {
            'Content-type': 'application/json',
            'apiKey': self.ofac_api_key
        }
        body = {
            'minScore': 95,
            'sources': ['sdn', 'nonsdn', 'un', 'ofsi', 'eu', 'dpl', 'sema', 'bfs', 'mxsat', 'lfiu'],
            'types': [ 'person', 'organization' ],
            'cases': cases
        }

        # send a post request to the OFAC API screening endpoint
        try:
            response = requests.post(
                self.ofac_api_url,
                json=body,
                headers=headers,
                timeout=self.OFAC_API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to reach the OFAC API: {err}")
            raise err

    def __transform_ofac_screening_response(
        self,
        people: List[Person]
    ) -> List[PersonScreeningResult]:
        """
        Transforms the OFAC screening response into a list of PersonScreeningResults 

        Args:
            people: A list of Person objects

        Returns:
            A list of PersonScreeningResults
        """
        response = self.__get_ofac_screening_response(people)
        if response['error']:
            raise self.OfacScreeningServiceError(f"OFAC API error: {response['errorMessage']}")

        person_screening_results = []
        results = response.get('results', [])
        for result in results:
            # gather relevant data related to the target person
            person_id = int(result['id'])
            country = self.person_map[person_id]['country']
            person_screening_result = {
                'id': person_id,
                'name_match': False,
                'dob_match': False,
                'country_match': False
            }

            # check all matches from OFAC
            matches = result.get('matches', [])
            for match in matches:
                # look for name and dob matches in the summary
                match_fields = match.get('matchSummary', {}).get('matchFields', [])
                self.__update_name_and_dob_match(person_screening_result, match_fields)

                # look for country matches in the sanction
                sanction = match.get('sanction', {})
                self.__update_country_match(person_screening_result, sanction, country)

            person_screening_results.append(person_screening_result)

        return person_screening_results

    # Public methods
    async def get_screening_results(self) -> List[PersonScreeningResult]:
        # get the results from people who were recently screened
        # and the people who were not recently screened
        cache_misses, cache_person_screening_results = await self._get_recently_screened_people()

        # only process the people who were not recently screened
        person_screening_results = self.__transform_ofac_screening_response(cache_misses)

        # update the redis cache with fresh screening results
        await self._update_screening_results_cache(person_screening_results)

        # store resuls in the database
        await self._store_screening_results(person_screening_results)

        # return the combined results
        return cache_person_screening_results + person_screening_results
