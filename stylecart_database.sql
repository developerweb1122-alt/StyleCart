CREATE DATABASE stylecart;

USE stylecart;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
USE stylecart;

SHOW TABLES;
SELECT * FROM users;
USE stylecart;

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id INT,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    stock INT DEFAULT 0,
    size VARCHAR(50),
    color VARCHAR(50),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);

SHOW TABLES;
DESCRIBE products;

USE stylecart;

CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

USE stylecart;

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) DEFAULT 'Pending',
    shipping_address VARCHAR(255),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);

use stylecart;
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

USE stylecart;

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Pending',
    transaction_id VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

use stylecart;
CREATE TABLE returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    reason VARCHAR(255),
    return_status VARCHAR(50) DEFAULT 'Requested',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

USE stylecart;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);
USE stylecart;

INSERT INTO categories (category_name, description)
VALUES
('Women', 'Women clothing'),
('Men', 'Men clothing'),
('Kids', 'Kids clothing');

SELECT * FROM categories;
USE stylecart;

SHOW TABLES;
USE stylecart;

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id INT,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    stock INT DEFAULT 0,
    size VARCHAR(50),
    color VARCHAR(50),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);
USE stylecart;

CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

USE stylecart;

CREATE TABLE returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    reason VARCHAR(255),
    return_status VARCHAR(50) DEFAULT 'Requested',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
USE stylecart;

DESCRIBE users;
USE stylecart;

-- 1. USERS
DESCRIBE users;

-- 2. CATEGORIES
DESCRIBE categories;

-- 3. PRODUCTS
DESCRIBE products;

-- 4. CART
DESCRIBE cart;

-- 5. ORDERS
DESCRIBE orders;

-- 6. ORDER ITEMS
DESCRIBE order_items;

-- 7. PAYMENTS
DESCRIBE payments;

-- 8. RETURNS
DESCRIBE returns;

USE stylecart;

INSERT INTO products
(product_name, category_id, description, price, discount, stock, size, color, image_url)
VALUES

(
    'Floral Summer Dress',
    (SELECT category_id FROM categories WHERE category_name = 'Women'),
    'Stylish floral summer dress for women',
    1499.00,
    10,
    20,
    'S,M,L,XL',
    'Pink',
    'images/floral-dress.jpg'
),

(
    'Women Casual Top',
    (SELECT category_id FROM categories WHERE category_name = 'Women'),
    'Comfortable casual top for women',
    799.00,
    5,
    30,
    'S,M,L,XL',
    'White',
    'images/casual-top.jpg'
),

(
    'Men Casual Shirt',
    (SELECT category_id FROM categories WHERE category_name = 'Men'),
    'Regular fit casual shirt for men',
    999.00,
    10,
    25,
    'M,L,XL',
    'Blue',
    'images/men-shirt.jpg'
),

(
    'Men Denim Jeans',
    (SELECT category_id FROM categories WHERE category_name = 'Men'),
    'Comfortable denim jeans for men',
    1599.00,
    15,
    20,
    '30,32,34,36',
    'Blue',
    'images/men-jeans.jpg'
),

(
    'Kids Party Dress',
    (SELECT category_id FROM categories WHERE category_name = 'Kids'),
    'Beautiful party wear dress for kids',
    1299.00,
    15,
    15,
    'S,M,L',
    'Red',
    'images/kids-dress.jpg'
);
SELECT * FROM products;

USE stylecart;

INSERT INTO users
(full_name, email, phone, password)
VALUES
('Rahul Sharma', 'rahul@gmail.com', '9876543210', 'rahul123'),
('Priya Singh', 'priya@gmail.com', '9876543211', 'priya123'),
('Anjali Verma', 'anjali@gmail.com', '9876543212', 'anjali123');

SELECT * FROM users;


USE stylecart;

INSERT INTO cart (user_id, product_id, quantity)
VALUES
(1, 1, 2),
(1, 3, 1),
(2, 2, 1);

SELECT * FROM cart;

USE stylecart;

INSERT INTO orders
(user_id, total_amount, order_status, shipping_address)
VALUES
(1, 3497.00, 'Pending', 'Ghaziabad, Uttar Pradesh'),
(2, 799.00, 'Confirmed', 'Delhi, India');

SELECT * FROM orders;

USE stylecart;

INSERT INTO order_items
(order_id, product_id, quantity, price)
VALUES
(1, 1, 2, 1499.00),
(1, 3, 1, 999.00),
(2, 2, 1, 799.00);
SELECT * FROM order_items;

USE stylecart;

INSERT INTO returns
(order_id, product_id, reason, return_status)
VALUES
(1, 1, 'Size issue', 'Requested'),
(2, 2, 'Product not suitable', 'Requested');

SELECT * FROM returns;
USE stylecart;

SELECT * FROM users;
USE stylecart;

SELECT * FROM products;

SELECT 
    product_id,
    product_name,
    category_id,
    price,
    discount,
    stock,
    size,
    color,
    image_url
FROM products;


USE stylecart;

DESCRIBE cart;

SELECT * FROM cart;

USE stylecart;

SELECT * FROM cart;

USE stylecart;

SELECT * FROM orders
ORDER BY order_id DESC;

SELECT * FROM order_items
ORDER BY order_item_id DESC;

SELECT * FROM payments
ORDER BY payment_id DESC;

use stylecart;
SELECT COUNT(*) AS total_products
FROM products;

USE stylecart;

ALTER TABLE products
ADD COLUMN status VARCHAR(20) DEFAULT 'Active';

SELECT * FROM products;

USE stylecart;

SELECT product_id, product_name, stock
FROM products;
USE stylecart;

SELECT
    user_id,
    full_name,
    email,
    phone,
    created_at
FROM users
ORDER BY user_id DESC;

USE stylecart;

SELECT * FROM orders;
SELECT * FROM order_items;

SELECT * FROM payments;

SELECT order_id, user_id, order_status
FROM orders
ORDER BY order_id DESC;
