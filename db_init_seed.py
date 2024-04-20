import enum
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa
import pandas as pd
import psycopg2

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)

# Create simple production e-commerce db
class Customer(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String, nullable=False)
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String, nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class Category(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String, nullable=False)

    def __init__(self, name):
        self.name = name

class Product(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(sa.ForeignKey('category.id'), nullable=False)
    name: Mapped[str] = mapped_column(db.String)
    price: Mapped[float] = mapped_column(db.Float)

    def __init__(self, name, category_id, price):
        self.category_id = category_id
        self.name = name
        self.price = price

class Status(enum.Enum):
    PENDING = 'pending'
    RECEIVED = 'received'
    SHIPPED = 'shipped'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

class Order(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(sa.ForeignKey('customer.id'), nullable=False)
    order_timestamp: Mapped[datetime] = mapped_column(server_default=sa.func.CURRENT_TIMESTAMP())
    status: Mapped[Status] = mapped_column(db.String, nullable=False)
    
    def __init__(self, customer_id, order_timestamp, status):
        self.customer_id = customer_id
        self.order_timestamp = order_timestamp
        self.status = status

class OrderItem(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey('order.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(sa.ForeignKey('product.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

def drop_tables():
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )
    cursor = connection.cursor()
    cursor.execute("""
    drop table if exists category cascade;
    drop table if exists customer cascade;
    drop table if exists "order" cascade;
    drop table if exists order_item cascade;
    drop table if exists product cascade;
    """)
    connection.commit()
    connection.close()
    cursor.close()

if __name__=="__main__":
    drop_tables()
    with app.app_context():
        db.create_all()

        # create customer
        customers = pd.read_csv('./seed/customers.csv')
        for i, row in customers.iterrows():
            db.session.add(Customer(name=row['name'], email=row['email'], password=row['password']))
        db.session.commit()

        # add product and category
        categories = pd.read_csv('./seed/categories.csv')
        for i, row in categories.iterrows():
            db.session.add(Category(name=row['name']))
        db.session.commit()
        
        products = pd.read_csv('./seed/products.csv')
        for i, row in products.iterrows():
            db.session.add(Product(category_id=row['category_id'],name=row['name'],price=row['price']))
        db.session.commit()
