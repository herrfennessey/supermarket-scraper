import logging
from datetime import datetime, timezone

from google.cloud import firestore
from google.cloud.firestore_v1 import WriteBatch

from search_dto import SearchDto, ProductDto

SEARCHES_COLLECTION = "searches-v1"
PRODUCTS_COLLECTION = "products-v1"

logger = logging.getLogger()


class FirestoreDao:
    def __init__(self):
        self.firestore_db = firestore.Client()
        self.current_batch = None

    def should_process_search(self, search_term):
        doc_ref = self._get_search_reference(search_term)
        doc = doc_ref.get()
        return not doc.exists or (datetime.now(timezone.utc) - doc.update_time).days >= 14

    def write_search_dto(self, search_dto: SearchDto):
        batch = self.firestore_db.batch()
        for product in search_dto.search_results:
            if product.write_document:
                self._write_product(batch, product)
            product.document_reference = self._get_product_reference(product.pid)
        batch.set(self._get_search_reference(search_dto.search_term),
                  search_dto.dict(include={'search_results': {'__all__': {'document_reference'}}}))
        batch.commit()

    def _write_product(self, batch: WriteBatch, product_dto: ProductDto):
        batch.set(self._get_product_reference(product_dto.pid),
                  product_dto.dict(exclude={"write_document", "document_reference"}))

    def _get_search_reference(self, search_term: str):
        return self.firestore_db.collection(SEARCHES_COLLECTION).document(search_term)

    def _get_product_reference(self, pid: str):
        return self.firestore_db.collection(PRODUCTS_COLLECTION).document(pid)
