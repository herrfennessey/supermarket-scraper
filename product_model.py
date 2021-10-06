from typing import List

from pydantic.main import BaseModel


class Product(BaseModel):
    pid: str
    store_name: str
    url: str
    product_name: str
    product_category: List[str]
