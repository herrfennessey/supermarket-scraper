import itertools
import logging
from string import ascii_lowercase

from firestore_dao import FirestoreDao
from web_dao import WebDao

logger = logging.getLogger()


class SearchHarvester:
    def __init__(self):
        self.firestore_dao = FirestoreDao()
        self.web_dao = WebDao()

    def process(self):
        for idx, seed_search in self._get_next_seed_search():
            try:
                search_suggestions = self.web_dao.harvest_search_suggestions(seed_search)
                for suggestion in search_suggestions:
                    search_term = suggestion.q
                    if self.firestore_dao.should_process_search(search_term):
                        search_dto = self.web_dao.process_search(search_term)
                        self.firestore_dao.write_search_dto(search_dto)
                        a = 5
            except Exception as e:
                print(e)

    def _get_next_seed_search(self):
        for idx, query_string in enumerate(
                itertools.islice(self._generate_random_letters(), self._get_max_permutations())):
            yield idx, query_string

    @staticmethod
    def _generate_random_letters():
        # Generate permutations of aaa, aab, aac ... zzz
        for size in itertools.count(1):
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)

    @staticmethod
    def _get_max_permutations(max_length=3):
        iterator = max_length
        max_perm = 0
        while iterator > 0:
            max_perm += len(ascii_lowercase) ** iterator
            iterator -= 1
        return max_perm


if __name__ == "__main__":
    manufacturer_remover = SearchHarvester()
    manufacturer_remover.process()
