from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
from datetime import date, datetime
import os


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Tanu@12345",
    "database": "stylecart"
}


# =========================================================
# CUSTOMER FOLDER
# =========================================================

BASE_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

CUSTOMER_FOLDER = os.path.join(
    BASE_FOLDER,
    "customer"
)


# =========================================================
# STARTUP FILE CHECK
# =========================================================

print()
print("======================================")
print("       STYLECART CUSTOMER FILES")
print("======================================")
print("Backend folder:")
print(os.path.dirname(__file__))
print()

print("Customer folder:")
print(CUSTOMER_FOLDER)
print()

print(
    "Customer folder exists:",
    os.path.isdir(CUSTOMER_FOLDER)
)

print(
    "home.html exists:",
    os.path.isfile(
        os.path.join(
            CUSTOMER_FOLDER,
            "home.html"
        )
    )
)

print(
    "order.html exists:",
    os.path.isfile(
        os.path.join(
            CUSTOMER_FOLDER,
            "order.html"
        )
    )
)

print(
    "returnexchange.html exists:",
    os.path.isfile(
        os.path.join(
            CUSTOMER_FOLDER,
            "returnexchange.html"
        )
    )
)

print("======================================")
print()


# =========================================================
# CUSTOMER HTML FILE ROUTES
# =========================================================

@app.route(
    "/customer/<path:filename>",
    methods=["GET"]
)
def serve_customer_file(filename):

    print()
    print("CUSTOMER FILE REQUEST:", filename)

    file_path = os.path.join(
        CUSTOMER_FOLDER,
        filename
    )

    print("FULL FILE PATH:", file_path)

    if not os.path.isfile(file_path):

        print("FILE NOT FOUND:", file_path)

        return jsonify({
            "success": False,
            "message": "Customer file not found.",
            "file": filename,
            "expected_path": file_path
        }), 404

    return send_from_directory(
        CUSTOMER_FOLDER,
        filename
    )


@app.route(
    "/customer/",
    methods=["GET"]
)
def serve_customer_home():

    home_file = os.path.join(
        CUSTOMER_FOLDER,
        "home.html"
    )

    if not os.path.isfile(home_file):

        return jsonify({
            "success": False,
            "message": "home.html not found.",
            "expected_path": home_file
        }), 404

    return send_from_directory(
        CUSTOMER_FOLDER,
        "home.html"
    )


# =========================================================
# DIRECT RETURN EXCHANGE PAGE
# =========================================================

@app.route(
    "/customer/returnexchange.html",
    methods=["GET"]
)
def return_exchange_page():

    file_path = os.path.join(
        CUSTOMER_FOLDER,
        "returnexchange.html"
    )

    print()
    print("RETURN / EXCHANGE PAGE")
    print("Path:", file_path)
    print(
        "Exists:",
        os.path.isfile(file_path)
    )

    if not os.path.isfile(file_path):

        return jsonify({
            "success": False,
            "message":
                "returnexchange.html not found.",
            "expected_path":
                file_path
        }), 404

    return send_from_directory(
        CUSTOMER_FOLDER,
        "returnexchange.html"
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    try:

        connection = mysql.connector.connect(
            **DB_CONFIG
        )

        return connection

    except Error as e:

        print(
            "MySQL connection error:",
            e
        )

        return None


# =========================================================
# DATABASE CHECK
# =========================================================

def check_db():

    connection = None

    try:

        connection = mysql.connector.connect(
            **DB_CONFIG
        )

        if connection.is_connected():

            print(
                "MySQL connected successfully."
            )

            return True

    except Error as e:

        print(
            "MySQL connection failed:",
            e
        )

    finally:

        if connection is not None:
            try:
                connection.close()
            except:
                pass

    return False


# =========================================================
# JSON SAFE
# =========================================================

def make_json_safe(value):

    if isinstance(
        value,
        Decimal
    ):
        return float(value)

    if isinstance(
        value,
        (date, datetime)
    ):
        return value.isoformat()

    return value


def make_row_json(row):

    if row is None:
        return None

    return {
        key: make_json_safe(value)
        for key, value in row.items()
    }


def make_rows_json(rows):

    return [
        make_row_json(row)
        for row in rows
    ]


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message":
            "StyleCart Backend Running!",
        "customer_url":
            "http://127.0.0.1:5000/customer/"
    })


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    data = request.get_json() or {}

    full_name = data.get(
        "full_name",
        data.get("name", "")
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip().lower()

    phone = data.get(
        "phone",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    if not full_name:
        return jsonify({
            "success": False,
            "message": "Full name is required."
        }), 400

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            return jsonify({
                "success": False,
                "message":
                    "Email already registered."
            }), 409

        cursor.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                phone,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                full_name,
                email,
                phone,
                password
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message":
                "Registration successful.",
            "user_id": user_id
        }), 201

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message":
                "Registration failed.",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():

    data = request.get_json() or {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    )

    if not email or not password:

        return jsonify({
            "success": False,
            "message":
                "Email and password are required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email,
                phone
            FROM users
            WHERE email = %s
            AND password = %s
            """,
            (
                email,
                password
            )
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message":
                    "Invalid email or password."
            }), 401

        return jsonify({
            "success": True,
            "message":
                "Login successful.",
            "user": make_row_json(user)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message":
                "Login failed.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CHECK EMAIL
# =========================================================

@app.route(
    "/api/check-email",
    methods=["POST"]
)
def check_email():

    data = request.get_json() or {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        return jsonify({
            "success": True,
            "exists": bool(user)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# RESET PASSWORD
# =========================================================

@app.route(
    "/api/reset-password",
    methods=["POST"]
)
def reset_password():

    data = request.get_json() or {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    new_password = data.get(
        "new_password",
        data.get("password", "")
    )

    if not email or not new_password:

        return jsonify({
            "success": False,
            "message":
                "Email and new password are required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE email = %s
            """,
            (
                new_password,
                email
            )
        )

        connection.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message":
                    "Email not found."
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Password updated successfully."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# PRODUCTS
# =========================================================


@app.route("/api/products", methods=["GET"])
def get_products():

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_name,
                p.category_id,
                c.category_name,
                p.description,
                p.price,
                p.discount,
                p.stock,
                p.size,
                p.color,
                p.image_url
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            ORDER BY p.product_id DESC
        """)

        products = cursor.fetchall()

        return jsonify({
            "success": True,
            "products": make_rows_json(products)
        })

    except Error as e:
        return jsonify({
            "success": False,
            "message": "Could not load products.",
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()

#==========================================================
# SINGLE PRODUCT
# =========================================================


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_single_product(product_id):

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_name,
                p.category_id,
                c.category_name,
                p.description,
                p.price,
                p.discount,
                p.stock,
                p.size,
                p.color,
                p.image_url,
                p.created_at,
                p.status
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            WHERE p.product_id = %s
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found."
            }), 404

        return jsonify({
            "success": True,
            "product": make_row_json(product)
        })

    except Error as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


   
          



# =========================================================
# CART - GET
# =========================================================

@app.route(
    "/api/cart/<int:user_id>",
    methods=["GET"]
)
def get_cart(user_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                c.cart_id,
                c.user_id,
                c.product_id,
                c.quantity,
                p.product_name,
                p.price,
                p.discount,
                p.image_url,
                p.stock,
                p.size,
                p.color
            FROM cart c
            JOIN products p
                ON c.product_id = p.product_id
            WHERE c.user_id = %s
            ORDER BY c.cart_id DESC
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        return jsonify({
            "success": True,
            "cart":
                make_rows_json(rows)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CART - ADD
# =========================================================

@app.route(
    "/api/cart",
    methods=["POST"]
)
def add_to_cart():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    product_id = data.get("product_id")
    quantity = int(
        data.get("quantity", 1)
    )

    if not user_id or not product_id:

        return jsonify({
            "success": False,
            "message":
                "user_id and product_id are required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                product_id,
                stock
            FROM products
            WHERE product_id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:

            return jsonify({
                "success": False,
                "message":
                    "Product not found."
            }), 404

        if product["stock"] < quantity:

            return jsonify({
                "success": False,
                "message":
                    "Not enough stock."
            }), 400

        cursor.execute(
            """
            SELECT
                cart_id,
                quantity
            FROM cart
            WHERE user_id = %s
            AND product_id = %s
            """,
            (
                user_id,
                product_id
            )
        )

        existing = cursor.fetchone()

        if existing:

            new_quantity = (
                existing["quantity"]
                + quantity
            )

            cursor.execute(
                """
                UPDATE cart
                SET quantity = %s
                WHERE cart_id = %s
                """,
                (
                    new_quantity,
                    existing["cart_id"]
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO cart
                (
                    user_id,
                    product_id,
                    quantity
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    product_id,
                    quantity
                )
            )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Product added to cart."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CART - UPDATE
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["PUT"]
)
def update_cart(cart_id):

    data = request.get_json() or {}

    quantity = data.get("quantity")

    if quantity is None:

        return jsonify({
            "success": False,
            "message":
                "Quantity is required."
        }), 400

    quantity = int(quantity)

    if quantity <= 0:

        return jsonify({
            "success": False,
            "message":
                "Quantity must be greater than 0."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE cart
            SET quantity = %s
            WHERE cart_id = %s
            """,
            (
                quantity,
                cart_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Cart updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CART - DELETE
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["DELETE"]
)
def delete_cart_item(cart_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM cart
            WHERE cart_id = %s
            """,
            (cart_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Cart item removed."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CLEAR CART
# =========================================================

@app.route(
    "/api/cart/user/<int:user_id>",
    methods=["DELETE"]
)
def clear_cart(user_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM cart
            WHERE user_id = %s
            """,
            (user_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Cart cleared."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# COUPON / OFFER VALIDATION
# =========================================================

@app.route(
    "/api/offers/validate",
    methods=["POST"]
)
def validate_offer():

    data = request.get_json() or {}

    code = data.get(
        "code",
        ""
    ).strip()

    subtotal = float(
        data.get("subtotal", 0)
    )

    if not code:

        return jsonify({
            "success": False,
            "message":
                "Coupon code is required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT *
            FROM offers
            WHERE offer_code = %s
            """,
            (code,)
        )

        offer = cursor.fetchone()

        if not offer:

            return jsonify({
                "success": False,
                "message":
                    "Invalid coupon code."
            }), 404

        status = str(
            offer.get("status", "Active")
        ).lower()

        if status not in [
            "active",
            "enabled",
            "1"
        ]:

            return jsonify({
                "success": False,
                "message":
                    "Coupon is inactive."
            }), 400

        discount_value = float(
            offer.get(
                "discount_value",
                offer.get("discount", 0)
            ) or 0
        )

        discount_type = str(
            offer.get(
                "discount_type",
                "percentage"
            )
        ).lower()

        if discount_type in [
            "percentage",
            "percent"
        ]:

            discount_amount = (
                subtotal
                * discount_value
                / 100
            )

        else:

            discount_amount = discount_value

        if discount_amount > subtotal:
            discount_amount = subtotal

        final_amount = (
            subtotal
            - discount_amount
        )

        return jsonify({
            "success": True,
            "message":
                "Coupon applied successfully.",
            "coupon_code": code,
            "discount_amount":
                round(
                    discount_amount,
                    2
                ),
            "final_amount":
                round(
                    final_amount,
                    2
                ),
            "offer":
                make_row_json(offer)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message":
                "Coupon validation failed.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================

# =========================================================
# PLACE ORDER
# =========================================================

@app.route("/api/orders", methods=["POST"])
def place_order():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id is required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # 1. GET CUSTOMER CART ITEMS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                c.cart_id,
                c.product_id,
                c.quantity,
                p.product_name,
                p.price,
                p.discount,
                p.stock
            FROM cart c
            JOIN products p
                ON c.product_id = p.product_id
            WHERE c.user_id = %s
            """,
            (user_id,)
        )

        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({
                "success": False,
                "message": "Cart is empty."
            }), 400

        # -------------------------------------------------
        # 2. VALIDATE CART AND CALCULATE SUBTOTAL
        # -------------------------------------------------

        subtotal = 0.0

        for item in cart_items:

            quantity = int(item.get("quantity") or 0)
            stock = int(item.get("stock") or 0)

            if quantity <= 0:
                return jsonify({
                    "success": False,
                    "message": (
                        f"Invalid quantity for "
                        f"{item['product_name']}."
                    )
                }), 400

            if stock < quantity:
                return jsonify({
                    "success": False,
                    "message": (
                        f"Not enough stock for "
                        f"{item['product_name']}. "
                        f"Available stock: {stock}."
                    )
                }), 400

            price = float(item.get("price") or 0)
            discount = float(item.get("discount") or 0)

            if price < 0 or discount < 0 or discount > 100:
                return jsonify({
                    "success": False,
                    "message": (
                        f"Invalid price or discount for "
                        f"{item['product_name']}."
                    )
                }), 400

            final_price = price * (1 - discount / 100)

            subtotal += final_price * quantity

        # -------------------------------------------------
        # 3. GET CHECKOUT DETAILS
        # -------------------------------------------------

        coupon_code = data.get("coupon_code") or None

        discount_amount = float(
            data.get("discount_amount", 0) or 0
        )

        if discount_amount < 0:
            return jsonify({
                "success": False,
                "message": "Invalid coupon discount."
            }), 400

        # Do not allow the discount to exceed the subtotal.
        discount_amount = min(discount_amount, subtotal)

        shipping_address = (
            data.get("shipping_address")
            or data.get("address")
            or ""
        )

        payment_method = (
            data.get("payment_method") or "COD"
        ).strip()

        if not payment_method:
            payment_method = "COD"

        final_total = round(
            max(0, subtotal - discount_amount), 2
        )

        # -------------------------------------------------
        # 4. CREATE ORDER
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO orders
            (
                user_id,
                total_amount,
                discount_amount,
                shipping_address,
                coupon_code,
                order_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                final_total,
                discount_amount,
                shipping_address,
                coupon_code,
                "Pending"
            )
        )

        order_id = cursor.lastrowid

        # -------------------------------------------------
        # 5. INSERT ORDER ITEMS AND UPDATE STOCK
        # -------------------------------------------------

        for item in cart_items:

            price = float(item.get("price") or 0)

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    item["product_id"],
                    int(item["quantity"]),
                    price
                )
            )

            cursor.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE product_id = %s
                  AND stock >= %s
                """,
                (
                    int(item["quantity"]),
                    item["product_id"],
                    int(item["quantity"])
                )
            )

            if cursor.rowcount != 1:
                raise Exception(
                    f"Stock update failed for "
                    f"{item['product_name']}."
                )

        # -------------------------------------------------
        # 6. INSERT PAYMENT RECORD
        # NOTE: Your payment table has no amount column.
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO payment
            (
                order_id,
                payment_method,
                payment_status
            )
            VALUES (%s, %s, %s)
            """,
            (
                order_id,
                payment_method,
                "Pending"
            )
        )

        # -------------------------------------------------
        # 7. CLEAR CUSTOMER CART
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM cart
            WHERE user_id = %s
            """,
            (user_id,)
        )

        # -------------------------------------------------
        # 8. SAVE EVERYTHING
        # -------------------------------------------------

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Order placed successfully.",
            "order_id": order_id,
            "subtotal": round(subtotal, 2),
            "discount_amount": round(discount_amount, 2),
            "total_amount": final_total,
            "order_status": "Pending",
            "payment_method": payment_method
        }), 201

    except Exception as e:

        if connection:
            connection.rollback()

        print("PLACE ORDER ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Order placement failed.",
            "error": str(e)
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()




# =========================================================
# CUSTOMER ORDERS
# =========================================================

@app.route(
    "/api/orders/<int:user_id>",
    methods=["GET"]
)
def get_user_orders(user_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                o.order_id,
                o.user_id,
                o.total_amount,
                o.discount_amount,
                o.shipping_address,
                o.coupon_code,
                o.order_status,
                o.order_date,

                p.payment_method,
                p.payment_status

            FROM orders o

            LEFT JOIN payment p
                ON o.order_id = p.order_id

            WHERE o.user_id = %s

            ORDER BY
                o.order_id DESC
            """,
            (user_id,)
        )

        orders = cursor.fetchall()

        for order in orders:

            cursor.execute(
                """
                SELECT
                    oi.order_item_id,
                    oi.order_id,
                    oi.product_id,
                    oi.quantity,
                    oi.price,
                    pr.product_name,
                    pr.image_url,
                    pr.size,
                    pr.color

                FROM order_items oi

                LEFT JOIN products pr
                    ON oi.product_id =
                       pr.product_id

                WHERE oi.order_id = %s
                """,
                (order["order_id"],)
            )

            order["items"] = (
                make_rows_json(
                    cursor.fetchall()
                )
            )

        return jsonify({
            "success": True,
            "orders":
                make_rows_json(orders)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message":
                "Could not load orders.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN ORDERS
# =========================================================

@app.route(
    "/api/admin/orders",
    methods=["GET"]
)
def admin_orders():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                o.order_id,
                o.user_id,
                u.full_name AS customer,
                u.email,
                o.order_date,
                o.total_amount,
                o.discount_amount,
                o.coupon_code,
                o.shipping_address,
                o.order_status,
                p.payment_method,
                p.payment_status

            FROM orders o

            LEFT JOIN users u
                ON o.user_id = u.user_id

            LEFT JOIN payment p
                ON o.order_id = p.order_id

            ORDER BY
                o.order_id DESC
            """
        )

        orders = cursor.fetchall()

        for order in orders:

            cursor.execute(
                """
                SELECT
                    oi.order_item_id,
                    oi.product_id,
                    oi.quantity,
                    oi.price,
                    pr.product_name,
                    pr.image_url

                FROM order_items oi

                LEFT JOIN products pr
                    ON oi.product_id =
                       pr.product_id

                WHERE oi.order_id = %s
                """,
                (order["order_id"],)
            )

            order["items"] = (
                make_rows_json(
                    cursor.fetchall()
                )
            )

        return jsonify({
            "success": True,
            "orders":
                make_rows_json(orders)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN SINGLE ORDER
# =========================================================

@app.route(
    "/api/admin/orders/<int:order_id>",
    methods=["GET"]
)
def admin_single_order(order_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                o.*,
                u.full_name AS customer,
                u.email,
                u.phone,
                p.payment_method,
                p.payment_status

            FROM orders o

            LEFT JOIN users u
                ON o.user_id = u.user_id

            LEFT JOIN payment p
                ON o.order_id = p.order_id

            WHERE o.order_id = %s
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if not order:

            return jsonify({
                "success": False,
                "message":
                    "Order not found."
            }), 404

        cursor.execute(
            """
            SELECT
                oi.*,
                pr.product_name,
                pr.image_url

            FROM order_items oi

            LEFT JOIN products pr
                ON oi.product_id =
                   pr.product_id

            WHERE oi.order_id = %s
            """,
            (order_id,)
        )

        order["items"] = (
            make_rows_json(
                cursor.fetchall()
            )
        )

        return jsonify({
            "success": True,
            "order":
                make_row_json(order)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN UPDATE ORDER STATUS
# =========================================================

@app.route(
    "/api/admin/orders/<int:order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):

    data = request.get_json() or {}

    status = data.get(
        "status",
        data.get("order_status")
    )

    if not status:

        return jsonify({
            "success": False,
            "message":
                "Order status is required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE orders
            SET order_status = %s
            WHERE order_id = %s
            """,
            (
                status,
                order_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message":
                    "Order not found."
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Order status updated.",
            "status": status
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN PAYMENT STATUS
# =========================================================

@app.route(
    "/api/admin/orders/<int:order_id>/payment-status",
    methods=["PUT"]
)
def update_payment_status(order_id):

    data = request.get_json() or {}

    payment_status = data.get(
        "payment_status",
        data.get("status")
    )

    if not payment_status:

        return jsonify({
            "success": False,
            "message":
                "Payment status is required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE payment
            SET payment_status = %s
            WHERE order_id = %s
            """,
            (
                payment_status,
                order_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Payment status updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN ORDER SUMMARY
# =========================================================

@app.route(
    "/api/admin/orders/summary",
    methods=["GET"]
)
def admin_order_summary():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_orders,

                SUM(
                    CASE
                        WHEN order_status =
                             'Pending'
                        THEN 1
                        ELSE 0
                    END
                ) AS pending_orders,

                SUM(
                    CASE
                        WHEN order_status =
                             'Delivered'
                        THEN 1
                        ELSE 0
                    END
                ) AS delivered_orders,

                COALESCE(
                    SUM(total_amount),
                    0
                ) AS total_sales

            FROM orders
            """
        )

        result = cursor.fetchone()

        return jsonify({
            "success": True,
            "summary":
                make_row_json(result)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN INVENTORY
# =========================================================

# =========================================================
# ADMIN INVENTORY
# =========================================================

@app.route("/api/admin/inventory", methods=["GET"])
def admin_inventory():
    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_name,
                p.category_id,
                c.category_name,
                p.stock,
                p.price,
                p.discount,
                p.image_url,
                p.status
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.category_id
            ORDER BY p.product_id DESC
        """)

        products = cursor.fetchall()

        return jsonify({
            "success": True,
            "inventory": make_rows_json(products)
        }), 200

    except Error as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()

# =========================================================
# ADMIN UPDATE INVENTORY
# =========================================================

@app.route(
    "/api/admin/inventory/<int:product_id>",
    methods=["PUT"]
)
def update_inventory(product_id):

    data = request.get_json() or {}

    stock = data.get("stock")

    if stock is None:

        return jsonify({
            "success": False,
            "message":
                "Stock is required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE products
            SET stock = %s
            WHERE product_id = %s
            """,
            (
                int(stock),
                product_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Inventory updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN CUSTOMERS
# =========================================================

@app.route(
    "/api/admin/customers",
    methods=["GET"]
)
def admin_customers():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                created_at
            FROM users
            ORDER BY user_id DESC
            """
        )

        customers = cursor.fetchall()

        return jsonify({
            "success": True,
            "customers":
                make_rows_json(customers)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN CUSTOMER STATUS
# =========================================================

@app.route(
    "/api/admin/customers/<int:user_id>/status",
    methods=["PUT"]
)
def update_customer_status(user_id):

    data = request.get_json() or {}

    status = data.get("status")

    # If users table has no status column,
    # return a clear response rather than crashing.

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE users
            SET status = %s
            WHERE user_id = %s
            """,
            (
                status,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Customer status updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message":
                "Customer status could not be updated.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN OFFERS
# =========================================================

@app.route(
    "/api/admin/offers",
    methods=["GET"]
)
def get_admin_offers():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT *
            FROM offers
            ORDER BY offer_id DESC
            """
        )

        offers = cursor.fetchall()

        return jsonify({
            "success": True,
            "offers":
                make_rows_json(offers)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN CREATE OFFER
# =========================================================

@app.route(
    "/api/admin/offers",
    methods=["POST"]
)
def create_offer():

    data = request.get_json() or {}

    offer_code = data.get(
        "offer_code",
        data.get("code", "")
    )

    discount_value = data.get(
        "discount_value",
        data.get("discount", 0)
    )

    discount_type = data.get(
        "discount_type",
        "percentage"
    )

    status = data.get(
        "status",
        "Active"
    )

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO offers
            (
                offer_code,
                discount_value,
                discount_type,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                offer_code,
                discount_value,
                discount_type,
                status
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Offer created successfully.",
            "offer_id":
                cursor.lastrowid
        }), 201

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message":
                "Offer creation failed.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN OFFER STATUS
# =========================================================

@app.route(
    "/api/admin/offers/<int:offer_id>/status",
    methods=["PUT"]
)
def update_offer_status(offer_id):

    data = request.get_json() or {}

    status = data.get(
        "status"
    )

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE offers
            SET status = %s
            WHERE offer_id = %s
            """,
            (
                status,
                offer_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Offer status updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN PROFILE
# =========================================================

@app.route(
    "/api/admin/profile",
    methods=["GET"]
)
def get_admin_profile():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email,
                phone
            FROM users
            ORDER BY user_id
            LIMIT 1
            """
        )

        profile = cursor.fetchone()

        return jsonify({
            "success": True,
            "profile":
                make_row_json(profile)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN PROFILE UPDATE
# =========================================================

@app.route(
    "/api/admin/profile",
    methods=["PUT"]
)
def update_admin_profile():

    data = request.get_json() or {}

    user_id = data.get("user_id")

    if not user_id:

        return jsonify({
            "success": False,
            "message":
                "user_id is required."
        }), 400

    full_name = data.get(
        "full_name",
        ""
    )

    email = data.get(
        "email",
        ""
    )

    phone = data.get(
        "phone",
        ""
    )

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE users
            SET
                full_name = %s,
                email = %s,
                phone = %s
            WHERE user_id = %s
            """,
            (
                full_name,
                email,
                phone,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Profile updated successfully."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN CHANGE PASSWORD
# =========================================================

@app.route(
    "/api/admin/change-password",
    methods=["PUT"]
)
def admin_change_password():

    data = request.get_json() or {}

    user_id = data.get("user_id")

    current_password = data.get(
        "current_password"
    )

    new_password = data.get(
        "new_password"
    )

    if (
        not user_id
        or not current_password
        or not new_password
    ):

        return jsonify({
            "success": False,
            "message":
                "All password fields are required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message":
                    "User not found."
            }), 404

        if user["password"] != current_password:

            return jsonify({
                "success": False,
                "message":
                    "Current password is incorrect."
            }), 401

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
            """,
            (
                new_password,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Password changed successfully."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# RETURN / EXCHANGE - CREATE REQUEST
# =========================================================

@app.route(
    "/api/return-requests",
    methods=["POST"]
)
def create_return_request():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    order_id = data.get("order_id")
    order_item_id = data.get(
        "order_item_id"
    )

    request_type = data.get(
        "request_type",
        data.get(
            "type",
            "Return"
        )
    )

    reason = data.get(
        "reason",
        ""
    )

    comment = data.get(
        "comment",
        ""
    )

    if not user_id or not order_id:

        return jsonify({
            "success": False,
            "message":
                "User ID and Order ID are required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # Check whether table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS return_requests
            (
                request_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_id INT NOT NULL,
                order_item_id INT NULL,
                request_type VARCHAR(30) DEFAULT 'Return',
                reason VARCHAR(255),
                comment TEXT,
                status VARCHAR(30) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        cursor.execute(
            """
            INSERT INTO return_requests
            (
                user_id,
                order_id,
                order_item_id,
                request_type,
                reason,
                comment,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                user_id,
                order_id,
                order_item_id,
                request_type,
                reason,
                comment,
                "Pending"
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Return/Exchange request submitted successfully.",
            "request_id":
                cursor.lastrowid
        }), 201

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message":
                "Return/Exchange request failed.",
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CUSTOMER RETURN REQUESTS
# =========================================================

@app.route(
    "/api/return-requests/<int:user_id>",
    methods=["GET"]
)
def get_return_requests(user_id):

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS return_requests
            (
                request_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_id INT NOT NULL,
                order_item_id INT NULL,
                request_type VARCHAR(30) DEFAULT 'Return',
                reason VARCHAR(255),
                comment TEXT,
                status VARCHAR(30) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        cursor.execute(
            """
            SELECT *
            FROM return_requests
            WHERE user_id = %s
            ORDER BY request_id DESC
            """,
            (user_id,)
        )

        requests = cursor.fetchall()

        return jsonify({
            "success": True,
            "requests":
                make_rows_json(requests)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN RETURN REQUESTS
# =========================================================

@app.route(
    "/api/admin/return-requests",
    methods=["GET"]
)
def admin_return_requests():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS return_requests
            (
                request_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_id INT NOT NULL,
                order_item_id INT NULL,
                request_type VARCHAR(30) DEFAULT 'Return',
                reason VARCHAR(255),
                comment TEXT,
                status VARCHAR(30) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        cursor.execute(
            """
            SELECT
                r.*,
                u.full_name AS customer,
                u.email

            FROM return_requests r

            LEFT JOIN users u
                ON r.user_id = u.user_id

            ORDER BY
                r.request_id DESC
            """
        )

        requests = cursor.fetchall()

        return jsonify({
            "success": True,
            "requests":
                make_rows_json(requests)
        })

    except Error as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN UPDATE RETURN REQUEST STATUS
# =========================================================

@app.route(
    "/api/admin/return-requests/<int:request_id>/status",
    methods=["PUT"]
)
def update_return_request_status(request_id):

    data = request.get_json() or {}

    status = data.get("status")

    if not status:

        return jsonify({
            "success": False,
            "message":
                "Status is required."
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message":
                "Database connection failed."
        }), 500

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE return_requests
            SET status = %s
            WHERE request_id = %s
            """,
            (
                status,
                request_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message":
                    "Return request not found."
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Return request status updated."
        })

    except Error as e:

        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "message":
            "Route not found.",
        "path":
            request.path
    }), 404


@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "message":
            "Internal server error.",
        "error":
            str(error)
    }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("          STYLECART BACKEND")
    print("======================================")
    print()

    print("Customer folder:")
    print(CUSTOMER_FOLDER)

    print()

    print(
        "Customer folder exists:",
        os.path.isdir(CUSTOMER_FOLDER)
    )

    print(
        "returnexchange.html exists:",
        os.path.isfile(
            os.path.join(
                CUSTOMER_FOLDER,
                "returnexchange.html"
            )
        )
    )

    print(
        "order.html exists:",
        os.path.isfile(
            os.path.join(
                CUSTOMER_FOLDER,
                "order.html"
            )
        )
    )

    print()

    if check_db():

        print("======================================")
        print("Server starting...")
        print()
        print(
            "Backend:"
            " http://127.0.0.1:5000"
        )
        print(
            "Customer:"
            " http://127.0.0.1:5000/customer/"
        )
        print(
            "Return/Exchange:"
            " http://127.0.0.1:5000/customer/returnexchange.html"
        )
        print("======================================")
        print()

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True
        )

    else:

        print()
        print(
            "SERVER NOT STARTED."
        )
        print(
            "MySQL connection failed."
        )