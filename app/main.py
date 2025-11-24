from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Backend", version="0.1.0")


class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: str | None = Field(None, max_length=255)


# Simple in-memory store adequate for demos; replace with a real DB in production.
ITEMS: Dict[int, Item] = {}


def _next_item_id() -> int:
    if not ITEMS:
        return 1
    return max(ITEMS) + 1


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", tags=["items"], response_model=Item, status_code=201)
def create_item(item: Item) -> Item:
    item_id = _next_item_id()
    ITEMS[item_id] = item
    return item


@app.get("/items/{item_id}", tags=["items"], response_model=Item)
def read_item(item_id: int) -> Item:
    item = ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
