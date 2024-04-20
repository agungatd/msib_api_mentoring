import json
from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

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

@app.route("/v1/")
def main():
    response = jsonify({
        'status': 200,
        'message': 'All is well :)'
    })

    # try to connect to database
    try:
        connection, cursor = db_conn()
        cursor.close()
        connection.close()
    except Exception as e:
        response = jsonify({
            'status': 500,
            'message': f'Error when connect to postgres: {e}'
        })

    return response

@app.route("/v1/customers", methods=['GET', 'POST', 'PUT', 'DELETE'])
def customer():
    data=[]
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute('SELECT * FROM customer')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    elif request.method == 'POST':
        cur.execute(
            """
            INSERT INTO customer 
            (name, email, password) 
            VALUES (%s, %s, %s)
            """,
            (request.form['name'], 
             request.form['email'], 
             request.form['password']),
        )
        conn.commit()
        return jsonify({'status': 200, 'message':'new customer has been inserted'})

    conn.close()
    cur.close()

@app.route("/v1/categories", methods=['GET', 'POST', 'PUT', 'DELETE'])
def category():
    data = []
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute(f'SELECT * FROM category')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    conn.close()
    cur.close()

@app.route("/v1/products", methods=['GET', 'POST', 'PUT', 'DELETE'])
def product():
    data = []
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute(f'SELECT * FROM product')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    conn.close()
    cur.close()

@app.route("/v1/product/<id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def product_by(id):
    data = []
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute(f'SELECT * FROM product WHERE id={id}')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    conn.close()
    cur.close()

@app.route("/v1/order/<id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def order_by(id):
    data=[]
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute(f'SELECT * FROM order WHERE id={id}')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    conn.close()
    cur.close()

@app.route("/v1/orders", methods=['GET', 'POST', 'PUT', 'DELETE'])
def order():
    data=[]
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute('SELECT * FROM "order"')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    elif request.method == 'POST':
        cur.execute(
            """
            INSERT INTO "order" 
            (customer_id, order_timestamp, status) 
            VALUES (%s, %s, %s)
            """,
            (request.form['customer_id'], 
             request.form['order_timestamp'], 
             request.form['status']),
        )
        conn.commit()
        return jsonify({'status': 200, 'message':'new order has been inserted'})

    conn.close()
    cur.close()

@app.route("/v1/order_items", methods=['GET', 'POST', 'PUT', 'DELETE'])
def order_item():
    data=[]
    conn, cur = db_conn()

    if request.method == 'GET':
        cur.execute('SELECT * FROM order_item')
        headers=[x[0] for x in cur.description]
        rows = cur.fetchall()

        for row in rows:
            data.append(dict(zip(headers,row)))
        return jsonify({'status': 200, 'message':'OK', 'data':data})
    
    elif request.method == 'POST':
        cur.execute(
            """
            INSERT INTO order_item 
            (order_id, product_id, quantity, price) 
            VALUES (%s, %s, %s, %s)
            """,
            (request.form['order_id'], 
             request.form['product_id'], 
             request.form['quantity'], 
             request.form['price']),
        )
        conn.commit()
        return jsonify({'status': 200, 'message':'new order item has been inserted'})

    conn.close()
    cur.close()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
