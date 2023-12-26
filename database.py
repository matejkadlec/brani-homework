from typing import List
from sqlalchemy import create_engine, func, ForeignKey, Table, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fastapi import HTTPException

# Create a base class for our models
Base = declarative_base()

# Check if association_table (junction table for Orders and Tags) already exists, if not create it
association_table = Base.metadata.tables.get('order_tags')
if association_table is None:
    association_table = Table('order_tags', Base.metadata,
        Column('order_id', Integer, ForeignKey('orders.id')),
        Column('tag_id', Integer, ForeignKey('tags.id'))
    )


# Define the Order model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    email = Column(String, nullable=False)
    tags = relationship('Tag', secondary=association_table, backref='orders')


# Define the Tag model
class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String, nullable=False)


# Connect to the SQLite database
engine = create_engine('sqlite:///sqlite.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_orders_with_tags() -> List[List[str]]:
    with Session() as session:
        # Get orders with all tags grouped together
        orders_data = (
            session.query(
                Order.id,
                Order.code,
                Order.date,
                Order.email,
                func.group_concat('🏷 ' + Tag.value, ', ').label('tags')
            )
            .select_from(Order)
            .join(association_table, Order.id == association_table.c.order_id)
            .join(Tag, Tag.id == association_table.c.tag_id)
            .group_by(Order.id, Order.code, Order.date, Order.email)
            .all()
        )

        # Prepare orders to correct format
        orders = [
            [
                order.id,
                order.code,
                order.date,
                order.email,
                order.tags
            ]
            for order in orders_data
        ]

        return orders


def get_tags_for_orders() -> List[List[str]]:
    with Session() as session:
        # Get all tags
        tag_data = session.query(Tag).all()

        # Prepare tags to correct format
        tags = [
            [
                tag.value
            ]
            for tag in tag_data
        ]

        return tags


def get_tags() -> List[dict[str, str | int]]:
    with Session() as session:
        # Get all tags
        tag_data = session.query(Tag).all()

        # Prepare tags to correct format
        tags = [
            {
                "id": tag.id,
                "value": tag.value
            }
            for tag in tag_data
        ]

        return tags


def create_tag_db(tag_value: str):
    with Session() as session:
        # Create new tag in the SQLite database
        try:
            new_tag = Tag(value=tag_value)
            session.add(new_tag)
            session.commit()
            return {"message": "New tag created successfully."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


def associate_tag_to_order(order_id: int, tag_id: int):
    with Session() as session:
        # Associate an order with a tag
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        tag = session.query(Tag).filter_by(id=tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        order.tags.append(tag)

        session.commit()
