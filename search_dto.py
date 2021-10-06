from typing import Optional, List

from google.cloud.firestore_v1 import DocumentReference
from pydantic import BaseModel


class ProductDto(BaseModel):
    pid: str
    store_name: str
    url: str
    product_name: str
    product_category: List[str]
    document_reference: Optional[DocumentReference] = None
    write_document: Optional[bool] = False

    class Config:
        # Allows for non basic types on the pydantic object
        arbitrary_types_allowed = True


class SearchDto(BaseModel):
    search_term: str
    search_results: List[ProductDto]
