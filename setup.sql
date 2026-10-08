-- 1. Setup Database
CREATE DATABASE IF NOT EXISTS SR_Hub_DB;
USE SR_Hub_DB;

-- 2. Reset Tables (Turn off safe mode to allow deletion)
SET SQL_SAFE_UPDATES = 0;
DROP TABLE IF EXISTS products;

-- 3. Create Product Table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    gender VARCHAR(20), 
    price INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    quantity INT DEFAULT 10,
    rating DECIMAL(2,1) DEFAULT 4.2
);

-- 4. Insert All 34 Items (8 Men, 8 Women, 8 Kids, 10 Accessories)
INSERT INTO products (name, category, gender, price, image_url, quantity, rating) VALUES 
-- ACCESSORIES (Mapped as per your specific request)
('Silk Hair Scrunchie', 'accessories', 'women', 199, 'acc1.jpeg', 15, 4.5),
('Designer Hair Clip', 'accessories', 'women', 299, 'acc2.jpeg', 10, 4.3),
('Kids Funky Watch', 'accessories', 'kids', 499, 'acc3.jpeg', 8, 4.7),
('Crystal Stud Earrings', 'accessories', 'women', 599, 'acc4.jpeg', 5, 4.2),
('Kids Cartoon Chain', 'accessories', 'kids', 399, 'acc5.jpeg', 12, 4.5),
('Sleek Silver Chain', 'accessories', 'men', 1299, 'acc6.jpeg', 5, 4.7),
('Classic Silver Watch', 'accessories', 'men', 2499, 'acc7.jpeg', 10, 4.8),
('Premium Leather Shoes', 'accessories', 'men', 2999, 'acc8.jpeg', 12, 4.9),
('Dynamic Sports Shoes', 'accessories', 'men', 1899, 'acc9.jpeg', 15, 4.6),
('Sleek Black Watch', 'accessories', 'women', 2199, 'acc10.jpeg', 8, 4.7),

-- MEN'S WEAR (8 Items)
('Veshti & Shirt Set', 'men', 'men', 1199, 'men1.jpeg', 15, 4.5),
('Pleated Shirt', 'men', 'men', 1499, 'men2.jpeg', 10, 4.2),
('Blue Men Kurta', 'men', 'men', 2100, 'men3.jpeg', 6, 4.8),
('Maroon Shirt', 'men', 'men', 5999, 'men4.jpeg', 4, 4.9),
('Baggy Hoddie', 'men', 'men', 1299, 'men5.jpeg', 15, 4.3),
('Cotton Cargo Pants', 'men', 'men', 1599, 'men6.jpeg', 10, 4.1),
('Traditional Kurta', 'men', 'men', 1800, 'men7.jpeg', 8, 4.5),
('Casual pants', 'men', 'men', 2400, 'men8.jpeg', 6, 4.7),

-- WOMEN'S WEAR (8 Items)
('Pink Salwar Set', 'women', 'women', 1599, 'women1.jpeg', 10, 4.5),
('Blue Floral Saree', 'women', 'women', 2299, 'women2.jpeg', 8, 4.2),
('Designer Gown', 'women', 'women', 4500, 'women3.jpeg', 5, 4.9),
('Casual Cotton Kurti', 'women', 'women', 799, 'women4.jpeg', 20, 4.2),
('Red Silk Saree', 'women', 'women', 3899, 'women5.jpeg', 5, 4.8),
('Pattu Saree', 'women', 'women', 5500, 'women6.jpeg', 3, 5.0),
('Party Wear Dress', 'women', 'women', 2100, 'women7.jpeg', 10, 4.4),
('Floral Anarkali', 'women', 'women', 2800, 'women8.jpeg', 7, 4.6),

-- KIDS' WEAR (8 Items)
('Sharara Set', 'kids', 'kids', 899, 'kids1.jpeg', 20, 4.5),
('A-Line Dress', 'kids', 'kids', 799, 'kids2.jpeg', 15, 4.3),
('Sweatshirt Set', 'kids', 'kids', 1899, 'kids3.jpeg', 10, 4.9),
('Boys Party Suit', 'kids', 'kids', 1499, 'kids4.jpeg', 10, 4.6),
('Girls Fairy Dress', 'kids', 'kids', 1299, 'kids5.jpeg', 12, 4.8),
('Cotton Romper', 'kids', 'kids', 599, 'kids6.jpeg', 25, 4.4),
('Denim Dungarees', 'kids', 'kids', 999, 'kids7.jpeg', 8, 4.3),
('Silk Pattu Pavadai', 'kids', 'kids', 1800, 'kids8.jpeg', 5, 4.9);

-- 5. Final Setup
SET SQL_SAFE_UPDATES = 1;

-- 6. Verification Queries (Check these in the output tab)
SELECT 'TOTAL PRODUCTS' as info, COUNT(*) FROM products;
SELECT category, gender, COUNT(*) FROM products GROUP BY category, gender;