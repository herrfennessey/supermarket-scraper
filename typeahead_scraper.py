import itertools
import logging
import time
from string import ascii_lowercase

import requests
from google.cloud import firestore
from pydantic import ValidationError
from requests import RequestException
from retrying import retry

from typeahead_response_model import ApiResponse

logger = logging.getLogger()

API_TEMPLATE_CALL = "https://suggest.dxpapi.com/api/v1/suggest/?account_id=6175&q={}&domain_key=albertsons"


class SearchHarvester:
    def __init__(self):
        super().__init__()
        self.number_of_letters = 3
        self.query_set = set()
        self.firestore_db = firestore.Client()

    @staticmethod
    def generate_random_letters():
        # Generate permutations of aaa, aab, aac ... zzz
        for size in itertools.count(1):
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)

    def _get_max_permutations(self):
        iterator = self.number_of_letters
        max_perm = 0
        while iterator > 0:
            max_perm += len(ascii_lowercase) ** iterator
            iterator -= 1
        return max_perm

    def harvest_search_terms(self):
        max_perms = self._get_max_permutations()
        for idx, query_string in enumerate(itertools.islice(self.generate_random_letters(), max_perms)):
            try:
                batch = self.firestore_db.batch()
                random_letter_response = self._make_requests(query_string)
                for real_search_term in random_letter_response.response.suggestions:
                    document_ref = self.firestore_db.collection("searches").document(real_search_term.q)
                    doc = document_ref.get()
                    if doc.exists:
                        logger.debug(f"{real_search_term.q} exists already - not fetching")
                        continue
                    else:
                        search_results = self._make_requests(real_search_term.q)
                        batch.set(document_ref, search_results.response.dict(exclude={"suggestions"}))
                        logger.debug(f"Wrote document: {real_search_term.q}")
                batch.commit()
            except RequestException as e:
                logger.warning(f"Error searching for {query_string} with exception: {e}")
            except ValidationError as e:
                logger.warning(f"Unable to serialize response for: {query_string} with exception: {e}")
            except Exception as e:
                logger.warning(f"Encountered unexpected exception searching for {query_string} with exception: {e}")

            if idx % 50 == 0 and idx > 0:
                print(f"{idx} completed! {max_perms - idx} to go!!")

    @staticmethod
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def _make_requests(search_term: str):
        time.sleep(.002)
        response = requests.get(API_TEMPLATE_CALL.format(search_term), timeout=3)
        return ApiResponse(**response.json())


if __name__ == "__main__":
    manufacturer_remover = SearchHarvester()
    manufacturer_remover.harvest_search_terms()
