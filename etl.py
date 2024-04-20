from datetime import datetime
import requests
import json
import pandas as pd
from sqlalchemy import create_engine

pd.set_option('display.max_columns', None)

def api_to_df(url):
    response = requests.get(url)
    resjson = json.loads(response.content)
    df = pd.DataFrame(data=resjson['data'])
    df = df.set_index('id')
    
    return df

def main():
    # EXTRACT
    api_endpoint = 'http://localhost:5000/v1'
    customers_df = api_to_df(f'{api_endpoint}/customers')
    products_df = api_to_df(f'{api_endpoint}/products')
    categories_df = api_to_df(f'{api_endpoint}/categories')
    orders_df = api_to_df(f'{api_endpoint}/orders')
    order_items_df = api_to_df(f'{api_endpoint}/order_items')

    # print(products_df.head())
    # print(order_items_df.head())
    # print(orders_df.head())
    # print(categories_df.head())

    # TRANSFORM
    ## Fact order table
    # 1. Join DataFrames using the merge() function
    fact_order = orders_df.merge(order_items_df, 
                                 left_on='id', 
                                 right_on='order_id', 
                                 how='left')  # Join order items
    # 2. select necessary columns only
    columns = ['order_id', 'customer_id', 'product_id', 'status', 'quantity', 'price']
    fact_order = fact_order[columns]

    # 3. calculate total amount (quantity x price)
    fact_order['total_amount'] = fact_order['quantity'] * fact_order['price']
    
    # 4. add createdat column
    fact_order['created_at'] = datetime.now()
    print(fact_order.head())

    # LOAD to Data Warehouse
    pgengine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/postgres')

    fact_order.to_sql('fact_order', pgengine, schema='dwh', if_exists='append', index=False)
    

if __name__ == "__main__":
    main()
