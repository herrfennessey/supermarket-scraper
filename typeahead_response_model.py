import json
from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    sale_price: float
    title: str
    url: str
    pid: str

    class Config:
        extra = "ignore"


class Suggestion(BaseModel):
    q: str

    class Config:
        extra = "ignore"


class ProductResponse(BaseModel):
    suggestions: Optional[list[Suggestion]] = []
    products: Optional[list[Product]] = []

    class Config:
        extra = "ignore"


class ApiResponse(BaseModel):
    response: Optional[ProductResponse] = ProductResponse()

    class Config:
        extra = "ignore"
