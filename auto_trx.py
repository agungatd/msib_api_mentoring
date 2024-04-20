from datetime import datetime, date
import requests
import psycopg2
from faker import Faker
import random
import json

def db_conn():
    try:
        connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="password",
            host="localhost",
            port="5432",
        )
        cursor = connection.cursor()
        return connection, cursor
    except Exception as e:
        raise e

def get_latest_order_id():
    response = requests.get(f'http://localhost:5000/v1/orders')
    resjson = json.loads(response.content)
    return max([ data['id'] for data in resjson['data']])

def get_max_cust():
    response = requests.get(f'http://localhost:5000/v1/customers')
    resjson = json.loads(response.content)
    return len(resjson['data'])

def get_product_price(id):
    if not isinstance(id, int):
        raise 'id must be integer'
    
    response = requests.get(f'http://localhost:5000/v1/product/{id}')
    resjson = json.loads(response.content)
    return resjson['data'][0]['price']

def post_random_orders(num_orders):
    url = 'http://localhost:5000/v1/orders'
    fake = Faker()
    statuses = ['pending', 'shipped', 'cancelled', 'completed', 'recieved']

    for order_no in range(num_orders):
        
        customer_id = random.randint(1, get_max_cust())
        order_timestamp = fake.date_time_between(start_date=date(2024,4,1))
        status = random.choice(statuses)
        num_items = random.randint(1,5)

        order = {
            'customer_id': customer_id,
            'order_timestamp': order_timestamp.isoformat(),
            'status': status
        }
        order_items = []
        for _ in range(num_items):
            product_id = random.randint(1,11)
            quantity = random.randint(1,3)
            price = get_product_price(product_id)

            order_items.append({
                'product_id':product_id,
                'quantity':quantity,
                'price':price
            })

        try:
            response = requests.post(url, data=order)
            response.raise_for_status()
            print(f"Order posted successfully for customer {customer_id}")

            latest_order_id = get_latest_order_id()
            for item in order_items:
                post_random_order_items(latest_order_id, item)
        except requests.exceptions.RequestException as e:
            print(f"Error posting order for customer {customer_id}: {e}")

def post_random_order_items(order_id, item):
    url = 'http://localhost:5000/v1/order_items'
    data = {
        'order_id': order_id,
        'product_id': int(item['product_id']),
        'quantity': int(item['quantity']),
        'price': float(item['price']),
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print(f"Order Item posted successfully for customer {order_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting order item for customer {order_id}: {e}")

if __name__ == "__main__":
    post_random_orders(10)