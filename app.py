import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","dev-secret-key")

# --- CONFIG FOR IMAGE UPLOADS ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database Connection Helper
def get_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ.get("DB_PASSWORD") 
            database="SR_Hub_DB",
            port=3306,
            connect_timeout=10
        )
        return db
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return None

# --- AUTHENTICATION ROUTES ---

@app.route("/")
def index():
    return render_template("splash.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        role = request.form.get('role')

        if role == 'vendor':
            if email == 'admin@srhub.com' and password == '1234':
                session['user'] = 'Admin'
                session['role'] = 'vendor'
                return redirect(url_for('vendor_dashboard'))
            else:
                flash("Incorrect Admin Credentials!", "error")
                return redirect(url_for('login'))
        else:
            if len(password) < 8:
                flash("Password must be at least 8 characters!", "error")
                return redirect(url_for('login'))
            
            session['user'] = email.split('@')[0] if '@' in email else email
            session['role'] = 'buyer'
            session['cart'] = []
            return redirect(url_for('home'))

    return render_template("login.html")

# --- NEW: GUEST ACCESS ---
@app.route("/guest_login")
def guest_login():
    session['user'] = "Guest"
    session['role'] = "buyer"
    session['cart'] = []
    return redirect(url_for('home'))

# --- NEW: REGISTER PAGE ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Logic to save user to DB would go here
        flash("Account created! You can now login.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- BUYER ROUTES ---

@app.route("/home")
def home():
    user_name = session.get('user', 'Guest')
    return render_template("home.html", user=user_name)

@app.route('/category/<name>')
def category(name):
    db = get_db()
    if not db: return "Database Connection Error"
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE category = %s", (name,))
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template(f"{name}.html", products=products)

@app.route("/search")
def search():
    user_query = request.args.get('query')
    db = get_db()
    if not db: return "Database Connection Error"
    cursor = db.cursor(dictionary=True)
    sql_search = "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s"
    search_value = f"%{user_query}%"
    cursor.execute(sql_search, (search_value, search_value))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("search_results.html", products=results, query=user_query)

# --- CART & CHECKOUT ---

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item = {
        "name": request.form.get("name"), 
        "price": int(request.form.get("price")),
        "image": request.form.get("image"), 
        "category": request.form.get("category"),
        "gender": request.form.get("gender"),
        "size": request.form.get("size"), 
        "qty": 1
    }
    cart = session.get('cart', [])
    cart.append(item)
    session['cart'] = cart
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['qty'] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout")
def checkout():
    cart = session.get('cart', [])
    if not cart: return redirect(url_for('home'))
    total = sum(item['price'] * item['qty'] for item in cart)
    return render_template("address.html", total=total)

@app.route("/place_order", methods=["POST", "GET"])
def place_order():
    cart = session.get('cart', [])
    if not cart: return redirect(url_for('home'))

    if request.method == "POST":
        session['shipping_info'] = {
            'cust_name': request.form.get('customer_name'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'payment_mode': request.form.get('payment_mode')
        }

    info = session.get('shipping_info')
    db = get_db()
    if not db: return "Database Error"
    cursor = db.cursor(dictionary=True)
    
    # Update quantities
    for item in cart:
        cursor.execute("UPDATE products SET quantity = quantity - 1 WHERE name = %s AND quantity > 0", (item['name'],))
    
    # 1. Get unique genders from the cart (Make sure add_to_cart saves 'gender'!)
    unique_genders = list(set([item.get('gender') for item in cart if item.get('gender')]))

    # --- START OF SMART RECOMMENDATION SECTION ---
    recs = []
    if unique_genders:
        for gen in unique_genders:
            # If 1 gender, get 3 items. If 2 genders, get 2 from first, 1 from second.
            limit = 3 if len(unique_genders) == 1 else (2 if gen == unique_genders[0] else 1)
            
            query = "SELECT * FROM products WHERE category='accessories' AND gender=%s AND quantity > 0 ORDER BY RAND() LIMIT %s"
            cursor.execute(query, (gen, limit))
            recs.extend(cursor.fetchall())
        
        # Shuffle them so they don't always appear in the same order
        random.shuffle(recs)
        recs = recs[:3] # Ensure exactly 3 items
    # --- END OF SMART RECOMMENDATION SECTION ---
    
    db.commit()
    cursor.close()
    db.close()

    # Calculation logic for the bill
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    discount = int(subtotal * 0.10)
    grand_total = subtotal - discount
    order_id = random.randint(10000, 99999)

    return render_template("bill.html", cart=cart, subtotal=subtotal, discount=discount, 
                           total=grand_total, recs=recs, order_id=order_id,
                           cust_name=info['cust_name'], phone=info['phone'], 
                           address=info['address'], payment_mode=info['payment_mode'])
@app.route("/order_success")
def order_success():
    session.pop('cart', None)
    return render_template("success.html")

# --- VENDOR DASHBOARD (LIST & ADD) ---
@app.route("/vendor/dashboard", methods=['GET', 'POST'])
def vendor_dashboard():
    # Security: Only allow Vendors
    if session.get('role') != 'vendor': 
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form.get('name')
        cat = request.form.get('category')
        prc = request.form.get('price')
        qty = request.form.get('quantity')
        
        # Handling the Image Upload
        file = request.files.get('image')
        if file and file.filename != '':
            img_filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            img_url = img_filename
        else:
            img_url = "default.jpg"

        # Insert new product
        cursor.execute("""
            INSERT INTO products (name, category, price, image_url, quantity, rating) 
            VALUES (%s, %s, %s, %s, %s, 4.0)
        """, (name, cat, prc, img_url, qty))
        db.commit()
        flash("Product Published Successfully!", "success")
        return redirect(url_for('vendor_dashboard'))
        
    # Fetch all products to display in the table
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("vendor_dashboard.html", products=products)

# --- UPDATE PRODUCT ROUTE ---
@app.route("/vendor/update", methods=['POST'])
def update_product():
    if session.get('role') != 'vendor': 
        return redirect(url_for('login'))
    
    # Getting the 5 fields from the modal form
    p_id = request.form.get('product_id')
    name = request.form.get('name')
    cat = request.form.get('category')  # <-- MAKE SURE THIS LINE IS HERE
    price = request.form.get('price')
    qty = request.form.get('quantity')
    
    db = get_db()
    cursor = db.cursor()
    
    # Updated SQL Query to include category
    sql = "UPDATE products SET name=%s, category=%s, price=%s, quantity=%s WHERE id=%s"
    cursor.execute(sql, (name, cat, price, qty, p_id))
    
    db.commit()
    cursor.close()
    db.close()
    
    flash("Product updated successfully!")
    return redirect(url_for('vendor_dashboard'))

# --- DELETE PRODUCT ROUTE ---
@app.route("/vendor/delete/<int:id>")
def delete_product(id):
    if session.get('role') != 'vendor': 
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    
    flash("Product deleted.")
    return redirect(url_for('vendor_dashboard'))
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
