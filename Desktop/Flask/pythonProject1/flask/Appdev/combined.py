from flask import Flask, render_template, request, redirect, url_for, session, flash
import shelve
import random
import uuid


app = Flask(__name__)
app.secret_key = 'supersecretkey'

SHELVE_DB = "auditions.db"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def form_audition():
    if request.method == 'POST':
        errors = {}

        # Validate Name (letters only)
        if not request.form['name'].replace(" ", "").isalpha():
            errors['name'] = "Only letters are allowed for Name."

        # Validate Nationality (letters only)
        if not request.form['nationality'].replace(" ", "").isalpha():
            errors['nationality'] = "Only letters are allowed for Nationality."

        # Validate Height (positive number)
        try:
            height = float(request.form['height'])
            if height <= 0:
                errors['height'] = "Height must be a positive number greater than zero."
        except ValueError:  # handle cases when the input is not a number
            errors['height'] = "Height must be a number."

        # Validate Weight (positive number)
        try:
            weight = float(request.form['weight'])
            if weight <= 0:
                errors['weight'] = "Weight must be a positive number greater than zero."
        except ValueError:
            errors['weight'] = "Weight must be a number."

        # Validate SMS/Contact (must be digits and max 8 characters)
        if not request.form['sms'].isdigit():
            errors['sms'] = "Only numbers are allowed for Contact."
        elif len(request.form['sms']) > 8:
            errors['sms'] = "Contact number cannot exceed 8 digits."

        # If there are errors, re-render the form with error messages
        if errors:
            return render_template('form_audition.html', errors=errors, entry=request.form)

        # Save data if no errors
        with shelve.open(SHELVE_DB) as db:
            new_id = str(len(db) + 1)
            db[new_id] = {
                'id': new_id,
                'name': request.form['name'],
                'email': request.form['email'],
                'birth_date': request.form['birth_date'],
                'nationality': request.form['nationality'],
                'gender': request.form['gender'],
                'height': request.form['height'],
                'weight': request.form['weight'],
                'sms': request.form['sms'],
                'introduction': request.form['introduction']
            }
        return redirect(url_for('home'))
    return render_template('form_audition.html')


@app.route('/terms')
def terms_and_agreement():
    return render_template('terms_and_agreement.html')


@app.route('/applicants')
def view_audition():
    with shelve.open(SHELVE_DB) as db:
        applicants = list(db.values())
    return render_template('view_audition.html', applicants=applicants)


@app.route('/edit/<string:applicant_id>', methods=['GET', 'POST'])
def edit_audition(applicant_id):
    with shelve.open(SHELVE_DB, writeback=True) as db:
        applicant = db.get(applicant_id)
        if applicant:
            if request.method == 'POST':
                applicant.update({
                    'name': request.form['name'],
                    'email': request.form['email'],
                    'birth_date': request.form['birth_date'],
                    'nationality': request.form['nationality'],
                    'gender': request.form['gender'],
                    'height': request.form['height'],
                    'weight': request.form['weight'],
                    'sms': request.form['sms'],
                    'introduction': request.form['introduction']
                })
                db[applicant_id] = applicant
                return redirect(url_for('view_audition'))
            return render_template('edit_audition.html', applicant=applicant)
    return "Applicant not found", 404


@app.route('/delete/<string:applicant_id>', methods=['POST'])
def delete_audition(applicant_id):
    with shelve.open(SHELVE_DB, writeback=True) as db:
        if applicant_id in db:
            del db[applicant_id]
            return redirect(url_for('view_audition'))
    return "Applicant not found", 404


def init_db(): #creates a db that looks like {'products': [], 'cart': [], 'users': {user: {'password': password, 'role': role}}}

    with shelve.open('shop_data') as db:
        if 'products' not in db:
            db['products'] = []
        if 'cart' not in db:
            db['cart'] = []
        if 'users' not in db:
            db['users'] = {"staff1": {"password": "staff123", "role": "admin"}}



@app.before_request
def setup():
    init_db() #creates the db


@app.route('/sustainability')
def sustainability():
    return render_template('sustainability.html')


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
            #flash("Failed to send OTP. Please try again later.", "error")
            #print(str(e))

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

        return render_template('login.html', error="Invalid username or password", errors={})

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('/'))



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
    errors = {}
    if request.method == 'POST':
        with shelve.open('shop_data') as db:
            cart = db.get('cart', [])

            name = request.form.get('name')
            address = request.form.get('address')
            if not request.form.get('card'):
                errors['card'] = "Card Number is required."
            elif not request.form.get('card').isdigit():
                errors['card'] = "Invalid Card Number. It must contain only digits."
            if not request.form.get('expiry'):
                errors['expiry'] = "Expiry date is required."
            elif not request.form.get('expiry').isdigit():
                errors['expiry'] = "Invalid Expiry. It must contain only numbers."
            if not request.form.get('cvv'):
                errors['cvv'] = "CVV is required."
            elif not request.form.get('cvv').isdigit() or len(request.form.get('cvv')) not in [3, 4]:
                errors['cvv'] = "Invalid CVV. Must be 3 or 4 digits."
            if errors:
                return render_template('checkout.html', errors=errors)
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

    return render_template('checkout.html', cart=cart_details, total=total, errors = {})


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
    if 'username' not in session or session['role'] != 'admin':
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
    errors = {}
    if request.method == 'POST':
        if len(request.form['username']) < 5:
            errors['username'] = 'Username needs to be at least 5 characters.'
        elif len(request.form['password']) < 8:
            errors['password'] = 'Password needs to be at least 8 characters.'
        if errors:
            return render_template('register.html', errors=errors)
        with shelve.open('shop_data') as db:
            users = db['users']
            if request.form['username'] in users:
                return "User already exists!"
            users[request.form['username']] = {"password": request.form['password'], "role": "customer"}
            db['users'] = users

        return redirect(url_for('login'))

    return render_template('register.html', errors={})


APPLICANTS_DB = "applicants.db"





@app.route('/courses')
def course_selection():
    """
    Page to display course categories and descriptions.
    """
    return render_template('courses.html')


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """
    Sign-up form to register for a course.
    """
    if request.method == 'POST':
        with shelve.open(APPLICANTS_DB) as db:
            new_id = str(len(db) + 1)
            db[new_id] = {
                'id': new_id,
                'name': request.form['name'],
                'email': request.form['email'],
                'age_group': request.form['age_group'],
                'mobile': request.form['mobile'],
                'course': request.form['course']
            }
        return redirect(url_for('view_applicants_courses'))
    return render_template('signup.html')


@app.route('/courses/applicants')
def view_applicants_courses():
    """
    Page to view all applicants with options to edit or delete.
    """
    with shelve.open(APPLICANTS_DB) as db:
        applicants = list(db.values())
    return render_template('applicants.html', applicants=applicants)


@app.route('/applicant/edit/<string:applicant_id>', methods=['GET', 'POST'])
def edit_applicant(applicant_id):
    """
    Page to edit applicant information.
    """
    with shelve.open(APPLICANTS_DB, writeback=True) as db:
        applicant = db.get(applicant_id)
        if applicant:
            if request.method == 'POST':
                applicant.update({
                    'name': request.form['name'],
                    'email': request.form['email'],
                    'age_group': request.form['age_group'],
                    'mobile': request.form['mobile'],
                    'course': request.form['course']
                })
                db[applicant_id] = applicant
                return redirect(url_for('view_applicants_courses'))
            return render_template('edit_applicants.html', applicant=applicant)
    return "Applicant not found", 404


@app.route('/applicant/delete/<string:applicant_id>', methods=['POST'])
def delete_applicant(applicant_id):
    """
    Delete an applicant.
    """
    with shelve.open(APPLICANTS_DB, writeback=True) as db:
        if applicant_id in db:
            del db[applicant_id]
            return redirect(url_for('view_applicants_courses'))
    return "Applicant not found", 404


@app.route('/competition')
def competition():
    return render_template('facilitate.html')

# Define a route for the virtual competition form, handling both GET and POST requests
@app.route('/virtual', methods=['GET', 'POST'])  # Route for the virtual competition form
def virtual_form():
    if request.method == 'POST':  # Check if the form was submitted via POST
        errors = {}  # Dictionary to store validation errors
        try:
            # Validate first name (letters only)
            if not request.form['first_name'].isalpha():
                errors['first_name'] = "Only letters are allowed for First Name."

            # Validate last name (letters only)
            if not request.form['last_name'].isalpha():
                errors['last_name'] = "Only letters are allowed for Last Name."

            # Validate phone number (digits only)
            if not request.form['phone'].isdigit():
                errors['phone'] = "Only numbers are allowed for Phone."

            # Validate ZIP code (digits only)
            if not request.form['zip'].isdigit():
                errors['zip'] = "Only numbers are allowed for ZIP."

            # If errors exist, re-render the form with error messages
            if errors:
                return render_template('virtual_form.html', errors=errors, entry=request.form)

            # Save data if no errors
            with shelve.open('competitions.db', writeback=True) as db:  # Open the shelve database
                if 'virtual' not in db:  # Check if the "virtual" competition category exists in the database
                    db['virtual'] = []  # Initialize the "virtual" competition category if not found

                # Create a new entry with form data
                new_entry = {
                    'id': str(uuid.uuid4()),
                    'first_name': request.form['first_name'],  # Get the first name from the form
                    'last_name': request.form['last_name'],  # Get the last name from the form
                    'birth_date': request.form['birth_date'],  # Get the birth date from the form
                    'gender': request.form['gender'],  # Get the gender from the form
                    'email': request.form['email'],  # Get the email from the form
                    'phone': request.form['phone'],  # Get the phone number from the form
                    'address': request.form['address'],  # Get the address from the form
                    'city': request.form['city'],  # Get the city from the form
                    'state': request.form['state'],  # Get the state from the form
                    'zip': request.form['zip'],  # Get the ZIP code from the form
                    'country': request.form['country']  # Get the country from the form
                }
                db['virtual'].append(new_entry)  # Add the new entry to the database
            flash('Virtual competition form submitted successfully!')  # Display a success message
            return redirect(url_for('view_competitions', competition_type='virtual'))  # Redirect to the view competitions page

        except Exception as e:  # Handle unexpected errors
            flash(f"An unexpected error occurred: {e}")


    return render_template('virtual_form.html', errors={}, entry=None)


@app.route('/physical', methods=['GET', 'POST'])  # Route for the physical competition form
def physical_form():
    if request.method == 'POST':  # Check if the form was submitted via POST
        errors = {}  # Dictionary to store validation errors
        try:
            # Validate first name (letters only)
            if not request.form['first_name'].isalpha():
                errors['first_name'] = "Only letters are allowed for First Name."

            # Validate last name (letters only)
            if not request.form['last_name'].isalpha():
                errors['last_name'] = "Only letters are allowed for Last Name."

            # Validate phone number (digits only)
            if not request.form['phone'].isdigit():
                errors['phone'] = "Only numbers are allowed for Phone."

            # Validate ZIP code (digits only)
            if not request.form['zip'].isdigit():
                errors['zip'] = "Only numbers are allowed for ZIP."

            # If errors exist, re-render the form with error messages
            if errors:
                return render_template('physical_form.html', errors=errors, entry=request.form)

            # Save data if no errors
            with shelve.open('competitions.db', writeback=True) as db:  # Open the shelve database
                if 'physical' not in db:  # Check if the "physical" competition category exists in the database
                    db['physical'] = []  # Initialize the "physical" competition category if not found

                # Create a new entry with form data
                new_entry = {
                    'id': str(uuid.uuid4()),  # Generate a unique ID for the entry
                    'first_name': request.form['first_name'],  # Get the first name from the form
                    'last_name': request.form['last_name'],  # Get the last name from the form
                    'birth_date': request.form['birth_date'],  # Get the birth date from the form
                    'gender': request.form['gender'],  # Get the gender from the form
                    'email': request.form['email'],  # Get the email from the form
                    'phone': request.form['phone'],  # Get the phone number from the form
                    'address': request.form['address'],  # Get the address from the form
                    'city': request.form['city'],  # Get the city from the form
                    'state': request.form['state'],  # Get the state from the form
                    'zip': request.form['zip'],  # Get the ZIP code from the form
                    'country': request.form['country']  # Get the country from the form
                }
                db['physical'].append(new_entry)  # Add the new entry to the database
            flash('Physical competition form submitted successfully!')  # Display a success message
            return redirect(url_for('view_competitions', competition_type='physical'))  # Redirect to the view competitions page

        except Exception as e:  # Handle unexpected errors
            flash(f"An unexpected error occurred: {e}")

    # Render the physical form template if the request method is GET
    return render_template('physical_form.html', errors={}, entry=None)  # Display the form for GET requests

# Define a route to view competition entries by competition type
@app.route('/view/<competition_type>')  # Route to view entries for a specific competition type
def view_competitions(competition_type):
    with shelve.open('competitions.db') as db:  # Open the shelve database
        entries = db.get(competition_type, [])  # Retrieve all entries for the specified competition type
    # Render the template to display entries, passing the competition type and entries
    return render_template('view_competitions.html', competition_type=competition_type, entries=entries)  # Display entries

# Define a route to edit a competition entry
@app.route('/edit/<competition_type>/<entry_id>', methods=['GET', 'POST'])  # Route to edit a specific entry
def edit_competition_entry(competition_type, entry_id):
    with shelve.open('competitions.db', writeback=True) as db:  # Open the shelve database
        entries = db.get(competition_type, [])  # Retrieve all entries for the specified competition type
        # Find the entry with the specified ID
        entry = next((entry for entry in entries if entry['id'] == entry_id), None)

        if not entry:  # If the entry does not exist, show an error
            flash("Entry not found!")  # Display an error message
            return redirect(url_for('view_competitions', competition_type=competition_type))  # Redirect to the entries page

        if request.method == 'POST':  # Handle form submission
            errors = {}  # Initialize an empty dictionary for validation errors
            try:
                # Validate first name (letters only)
                if not request.form['first_name'].isalpha():
                    errors['first_name'] = "Only letters are allowed for First Name."

                # Validate last name (letters only)
                if not request.form['last_name'].isalpha():
                    errors['last_name'] = "Only letters are allowed for Last Name."

                # Validate phone number (digits only)
                if not request.form['phone'].isdigit():
                    errors['phone'] = "Only numbers are allowed for Phone."

                # Validate ZIP code (digits only)
                if not request.form['zip'].isdigit():
                    errors['zip'] = "Only numbers are allowed for ZIP."

                # If there are validation errors, re-render the form with errors and entry data
                if errors:
                    return render_template(
                        f"{competition_type}_form.html",  # Dynamic form template based on competition type
                        entry=request.form,  # Pass form data
                        errors=errors  # Pass validation errors
                    )

                # Update the entry with the new form data
                entry.update({
                    'first_name': request.form['first_name'],  # Update the first name
                    'last_name': request.form['last_name'],  # Update the last name
                    'birth_date': request.form['birth_date'],  # Update the birth date
                    'gender': request.form['gender'],  # Update the gender
                    'email': request.form['email'],  # Update the email
                    'phone': request.form['phone'],  # Update the phone number
                    'address': request.form['address'],  # Update the address
                    'city': request.form['city'],  # Update the city
                    'state': request.form['state'],  # Update the state
                    'zip': request.form['zip'],  # Update the ZIP code
                    'country': request.form['country']  # Update the country
                })
                flash(f'{competition_type.capitalize()} entry updated successfully!')  # Display a success message
                return redirect(url_for('view_competitions', competition_type=competition_type))  # Redirect to entries page

            except Exception as e:  # Handle unexpected errors
                flash(f"An unexpected error occurred: {e}")

        # Render the form template with the current entry data for GET requests
        return render_template(
            f"{competition_type}_form.html",  # Dynamic form template
            entry=entry,  # Pass the current entry data
            errors={}  # Pass an empty errors dictionary
        )

# Define a route to delete a competition entry
@app.route('/delete/<competition_type>/<entry_id>')  # Route to delete a specific entry
def delete_entry(competition_type, entry_id):
    with shelve.open('competitions.db', writeback=True) as db:  # Open the shelve database
        if competition_type in db:  # Check if the competition type exists in the database
            # Filter out the entry with the specified ID
            db[competition_type] = [entry for entry in db[competition_type] if entry['id'] != entry_id]
    flash(f'{competition_type.capitalize()} entry deleted successfully!')  # Display a success message
    # Redirect to the view competitions page for the specified competition type
    return redirect(url_for('view_competitions', competition_type=competition_type))  # Redirect to entries page

# Define a route for the "About Competitions" page
@app.route('/about_competitions')  # Route for the about competitions page
def about_competitions():
    # Render the "About Competitions" template
    return render_template('about_competitions.html')  # Display the about competitions template


@app.route('/artist_contract', methods=['GET', 'POST'])
def artist_contract():
    with shelve.open('app_data') as db:
        if 'contracts' not in db:
            db['contracts'] = []

        if request.method == 'POST':
            errors = {}
            name = request.form['contract_name']
            email = request.form['email']
            venue_location = request.form['venue_location']
            country = request.form['country']
            phone_number = request.form['phone_number']
            if not name.isalpha():
                errors['name'] = 'Invalid Name'
            elif not country.isalpha():
                errors['country'] = 'Invalid Country'
            if errors:
                return render_template('artist_contract.html', errors=errors)
            new_contract = {
                'id': len(db['contracts']) + 1,
                'name': name,
                'email': email,
                'venue_location': venue_location,
                'country': country,
                'phone_number': phone_number
            }

            contracts = db['contracts']
            contracts.append(new_contract)
            db['contracts'] = contracts

        contracts = db['contracts']

    return render_template('artist_contract.html', contracts=contracts, errors={})


@app.route('/artist_contract/delete/<int:id>')
def delete_artist_contract(id):
    with shelve.open('app_data') as db:
        if 'contracts' in db:
            contracts = db['contracts']
            contracts = [c for c in contracts if c['id'] != id]
            db['contracts'] = contracts

    return redirect(url_for('artist_contract'))


@app.route('/artist_contract/edit/<int:id>', methods=['GET', 'POST'])
def edit_artist_contract(id):
    with shelve.open('app_data') as db:
        if 'contracts' in db:
            contracts = db['contracts']

            contract = next((c for c in contracts if c['id'] == id), None)
            if request.method == 'POST' and contract:
                contract['name'] = request.form['contract_name']
                contract['email'] = request.form['email']
                contract['venue_location'] = request.form['venue_location']
                contract['country'] = request.form['country']
                contract['phone_number'] = request.form['phone_number']

                db['contracts'] = contracts
                return redirect(url_for('artist_contract'))

    return render_template('edit_contract.html', contract=contract)


@app.route('/live_calendar', methods=['GET', 'POST'])
def live_calendar():
    with shelve.open('app_data') as db:
        if 'events' not in db:
            db['events'] = []

        if request.method == 'POST':
            event_name = request.form['event_name']
            event_date = request.form['event_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            new_event = {
                'id': len(db['events']) + 1,
                'name': event_name,
                'event_date': event_date,
                'start_time': start_time,
                'end_time': end_time
            }

            events = db['events']
            events.append(new_event)
            db['events'] = events

        events = db['events']

    return render_template('live_calendar.html', events=events)


@app.route('/live_calendar/delete/<int:id>')
def delete_live_calendar_event(id):
    with shelve.open('app_data') as db:
        if 'events' in db:
            events = db['events']
            events = [e for e in events if e['id'] != id]
            db['events'] = events

    return redirect(url_for('live_calendar'))


@app.route('/live_calendar/edit/<int:id>', methods=['GET', 'POST'])
def edit_live_calendar_event(id):
    with shelve.open('app_data') as db:
        if 'events' in db:
            events = db['events']
            event = next((e for e in events if e['id'] == id), None)

            if request.method == 'POST' and event:
                event['name'] = request.form['event_name']
                event['event_date'] = request.form['event_date']
                event['start_time'] = request.form['start_time']
                event['end_time'] = request.form['end_time']

                db['events'] = events
                return redirect(url_for('live_calendar'))

    return render_template('edit_event.html', event=event)


if __name__ == '__main__':
    app.run(debug=False)     