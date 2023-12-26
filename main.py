from database import get_orders_with_tags, get_tags_for_orders, get_tags, create_tag_db, associate_tag_to_order
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TagInput for creating tags
class TagInput(BaseModel):
    tag_value: str


# OrderTagInput for adding tags to orders
class OrderTagInput(BaseModel):
    order_id: int
    tag_id: int


# Default endpoint showing tags and orders
@app.get("/")
def main():
    return {"tags": get_tags_for_orders(), "orders": get_orders_with_tags()}


# create_tag endpoint for creating tags
@app.post("/create_tag/")
async def create_tag(tag_input: TagInput):
    create_tag_db(tag_input.tag_value)
    return {"message": "Tag created successfully."}


# tags endpoint for fetching tags
@app.get("/tags/")
def fetch_tags():
    return {"tags": get_tags()}


# associate_tag endpoint for associating an order with a tag
@app.post("/associate_tag/")
async def associate_tag(order_tag: OrderTagInput):
    associate_tag_to_order(order_tag.order_id, order_tag.tag_id)
    return {"message": "Tag associated with the order successfully."}


