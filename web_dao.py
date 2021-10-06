import logging
import time

import requests
from retrying import retry

from albertson_pdp_parser import parse_pdp_response
from search_dto import SearchDto, ProductDto
from typeahead_response_model import ApiResponse

SEARCHES_COLLECTION = "searches-v1"
PRODUCTS_COLLECTION = "products-v1"
API_TEMPLATE_CALL = "https://suggest.dxpapi.com/api/v1/suggest/?account_id=6175&q={}&domain_key=albertsons"
ALBERTSONS_PRODUCT_DETAIL_PAGE = "https://www.albertsons.com/shop/product-details.{}.html"

logger = logging.getLogger()


class WebDao:
    def __init__(self):
        self.product_cache = ProductMemoryCache()

    def harvest_search_suggestions(self, search_term):
        return self._make_api_request(search_term).response.suggestions

    def process_search(self, search_term):
        search_results = self._make_api_request(search_term)
        search_dto = SearchDto(search_term=search_term, search_results=[])
        for product in search_results.response.products:
            product_dto = self.product_cache.get_product(product.pid)
            if product_dto:
                search_dto.search_results.append(product_dto)
        return search_dto

    @staticmethod
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def _make_api_request(search_term: str):
        # 5 ms
        time.sleep(.005)
        response = requests.get(API_TEMPLATE_CALL.format(search_term), timeout=3)
        return ApiResponse(**response.json())


class ProductMemoryCache:
    def __init__(self):
        self.cache = {}

    def get_product(self, pid):
        if pid in self.cache:
            product = self.cache.get(pid)
            product.write_document = False
        else:
            try:
                product = ProductDto(**self._make_pdp_request(pid))
                self.cache[pid] = product
                product.write_document = True
            except Exception as e:
                logger.warning(f"Unable to parse PDP page for pid: {pid}")
                return None
        return product

    @staticmethod
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def _make_pdp_request(pid: str):
        # 20 ms
        time.sleep(.02)
        url = ALBERTSONS_PRODUCT_DETAIL_PAGE.format(pid)
        response = requests.get(url, timeout=3)
        return parse_pdp_response(pid, url, response)
