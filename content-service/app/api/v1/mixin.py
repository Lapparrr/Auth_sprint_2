from pydantic import BaseModel
from typing import List


class MyPage(BaseModel):
    items: List
    total: int
    page_size: int
    page_number: int


def create_page(items, total, params) -> MyPage:
    return MyPage(
        items=items,
        total=total,
        page_size=params.page_size,
        page_number=params.page_number,
    )
