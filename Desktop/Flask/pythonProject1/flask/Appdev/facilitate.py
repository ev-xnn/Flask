# Import necessary modules from Flask
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask utilities for building web apps
# Import shelve for persistent storage and uuid for generating unique IDs
import shelve  # Provides a persistent dictionary-like storage
import uuid  # For generating unique IDs for each entry

# Create a Flask application instance
app = Flask(__name__)  # Initialize the Flask app
# Set a secret key for securely signing the session cookie
app.secret_key = 'secret_key'  # Secret key for session and flash message security

# Define a route for the homepage
@app.route('/')  # Route for the root URL
def facilitate():
    # Render the homepage template
    return render_template('facilitate.html')  # Display the facilitate.html template

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
                db['virtual'].append(new_entry)  # Add the new entry to the database
            flash('Virtual competition form submitted successfully!')  # Display a success message
            return redirect(url_for('view_competitions', competition_type='virtual'))  # Redirect to the view competitions page

        except Exception as e:  # Handle unexpected errors
            flash(f"An unexpected error occurred: {e}")

    # Render the virtual form template if the request method is GET
    return render_template('virtual_form.html', errors={}, entry=None)  # Display the form for GET requests

# Define a route for the physical competition form, handling both GET and POST requests
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

# Run the Flask application in debug mode when the script is executed directly
if __name__ == '__main__':  # Check if the script is run directly
    app.run(debug=True)  # Run the Flask application in debug mode
