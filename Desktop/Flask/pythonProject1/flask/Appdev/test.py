import shelve
from flask import Flask, render_template, request, redirect, url_for, session, flash
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'


def init_db(): #creates a db that looks like {'products': [], 'cart': [], 'users': {user: {'password': password, 'role': role}}}

    with shelve.open('shop_data') as db:
        if 'products' not in db:
            db['products'] = []
        if 'cart' not in db:
            db['cart'] = []
        if 'users' not in db:
            db['users'] = {"staff1": {"password": "staff123", "role": "admin", "phone": "+6581237524"}}



@app.before_request
def setup():
    init_db() #creates the db


@app.route('/')
def home():
    return redirect(url_for('shop')) #shows homepage


@app.route('/shop')
def shop():
    with shelve.open('shop_data') as db:
        products = db['products'] #opens the db and assigns products stored in the db as products
    return render_template('shop.html', products=products)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')

        with shelve.open('shop_data') as db:
            users = db.get('users', {})
            user = users.get(username)

            if not user:
                flash("User not found!", "error")
                return redirect(url_for('forgot_password'))

            # Generate a random 6-digit OTP
            otp = random.randint(100000, 999999)

            # Send the OTP via SMS using Twilio


                # Store OTP temporarily
            user['otp'] = otp
            db['users'] = users
            flash("OTP sent to your registered phone number.", "success")
            return redirect(url_for('verify_otp', username=username))
            flash("Failed to send OTP. Please try again later.", "error")
            print(str(e))

    return render_template('forgot_password.html')


@app.route('/verify-otp/<username>', methods=['GET', 'POST'])
def verify_otp(username):
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('new_password')

        with shelve.open('shop_data') as db:
            users = db.get('users', {})
            user = users.get(username)

            if not user or 'otp' not in user or str(user['otp']) != otp:
                flash("Invalid OTP. Please try again.", "error")
                return redirect(url_for('verify_otp', username=username))

            # Update password and clear OTP
            user['password'] = new_password
            del user['otp']
            db['users'] = users

            flash("Password reset successfully. You can now log in.", "success")
            return redirect(url_for('login'))

    return render_template('verify_otp.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': #checks if the form is submitted
        username = request.form.get('username') #gets username
        password = request.form.get('password') #gets password

        # Open the Shelve database to access users
        with shelve.open('shop_data') as db:
            users = db.get('users', {}) #assigns the users db to the variable users
            user = users.get(username)  # Look for the user in the database
            if user and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']  # Save the user's role in the session
                return redirect(url_for('staff') if user['role'] == 'admin' else url_for('shop')) #redirects to staff page if the role is admin, else redirect to the shop

        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('shop'))



@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id')) #finds the product id of the submitted form and converts it into an integer
    quantity = int(request.form.get('quantity', 1)) #finds the quantity of the products added and converts it into an integer

    with shelve.open('shop_data') as db:
        products = db['products']
        cart = db['cart']
        product = next((p for p in products if p['id'] == product_id), None) #next() returns the first matching product or None if there is nothing found and checks if the id matches the product id
        if product: #if product is not None
            cart_item = next((item for item in cart if item['product_id'] == product_id), None) #finds if there is a product in cart that matches the id, and returns None if there isn't
            if cart_item:
                cart_item['quantity'] += quantity #adds the quantity if the item is already in the cart
            else:
                cart.append({"product_id": product_id, "quantity": quantity}) #creates a new item and adds the id and quantity
            db['cart'] = cart
            return '', 200

    return '', 404




@app.route('/cart')
def view_cart():
    with shelve.open('shop_data') as db:
        products = db['products']
        cart = db['cart']
        cart_details = []
        total = 0
        for item in cart:
            product = next((p for p in products if p['id'] == item['product_id']), None)
            if product:
                subtotal = product['price'] * item['quantity']
                total += subtotal
                cart_details.append({
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": item['quantity'],
                    "image": product['image'],
                    "total": subtotal,
                    "product_id": item['product_id']
                })
    return render_template('view_cart.html', cart=cart_details, total=total)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    with shelve.open('shop_data') as db:
        cart = db.get('cart', [])

        if request.method == 'POST':
            name = request.form.get('name')
            address = request.form.get('address')
            card = request.form.get('card')
            expiry = request.form.get('expiry')
            cvv = request.form.get('cvv')

            if not (name and address and card and expiry and cvv):
                flash("All fields are required.", "error")
                return redirect(url_for('checkout'))

            # Simulate order placement and clear cart
            total = 0
            cart_details = []
            for item in cart:
                product = next((p for p in db['products'] if p['id'] == item['product_id']), None)
                if product:
                    subtotal = product['price'] * item['quantity']
                    total += subtotal
                    cart_details.append({
                        "name": product['name'],
                        "price": product['price'],
                        "quantity": item['quantity'],
                        "total": subtotal
                    })

            db['cart'] = []

            return render_template('order_confirmation.html', cart=cart_details, total=total)

        # Calculate total
        total = 0
        cart_details = []
        for item in cart:
            product = next((p for p in db['products'] if p['id'] == item['product_id']), None)
            if product:
                subtotal = product['price'] * item['quantity']
                total += subtotal
                cart_details.append({
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": item['quantity'],
                    "total": subtotal
                })

    return render_template('checkout.html', cart=cart_details, total=total)


@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))

    with shelve.open('shop_data') as db:
        cart = db['cart']
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                break
        db['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/delete-from-cart', methods=['POST'])
def delete_from_cart():
    product_id = int(request.form.get('product_id'))

    with shelve.open('shop_data') as db:
        cart = db['cart']
        cart = [item for item in cart if item['product_id'] != product_id]
        db['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/staff', methods=['GET', 'POST'])
def staff():
    if 'username' not in session or session['username'] != 'staff1':
        return redirect(url_for('login'))

    with shelve.open('shop_data') as db:
        products = db['products']

        if request.method == 'POST':
            product_name = request.form.get('product_name')
            product_price = round(float(request.form.get('product_price')))
            product_image = request.form.get('product_image')

            new_product = {
                "id": len(products) + 1,
                "name": product_name,
                "price": product_price,
                "image": product_image
            }
            products.append(new_product)
            db['products'] = products

    return render_template('staff.html', products=products)


@app.route('/update-product', methods=['POST'])
def update_product():
    product_id = int(request.form.get('product_id'))
    product_name = request.form.get('product_name')
    product_price = float(request.form.get('product_price'))
    product_image = request.form.get('product_image')

    with shelve.open('shop_data') as db:
        products = db['products']
        for product in products:
            if product['id'] == product_id:
                product['name'] = product_name
                product['price'] = product_price
                product['image'] = product_image
                break
        db['products'] = products
    return redirect(url_for('staff'))


@app.route('/delete-product', methods=['POST'])
def delete_product():
    product_id = int(request.form.get('product_id'))

    with shelve.open('shop_data') as db:
        products = db['products']
        products = [product for product in products if product['id'] != product_id]
        db['products'] = products
    return redirect(url_for('staff'))


@app.route('/details', methods=['GET', 'POST'])
def details():
    if 'username' not in session or session.get('role') != 'admin':
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login'))
    with shelve.open('shop_data') as db:
        users = db['users']
        if request.method == 'POST':
            action = request.form.get('action')
            username = request.form.get('username')

            if action == 'create':
                password = request.form.get('password')
                role = request.form.get('role')
                if username not in users:
                    users[username] = {"password": password, "role": role}
                else:
                    return "User already exists!"

            elif action == 'update':
                if username in users:
                    users[username]['password'] = request.form.get('password', users[username]['password'])
                    users[username]['role'] = request.form.get('role', users[username]['role'])
                else:
                    return "User not found!"

            elif action == 'delete':
                if username in users:
                    del users[username]
                else:
                    return "User not found!"

            db['users'] = users

        return render_template('details.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with shelve.open('shop_data') as db:
            users = db['users']
            if username in users:
                return "User already exists!"
            users[username] = {"password": password, "role": "customer"}
            db['users'] = users

        return redirect(url_for('login'))

    return render_template('register.html')




if __name__ == '__main__':
    app.run(debug=False)
