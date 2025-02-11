# Import necessary modules from Flask
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask framework utilities for web app development
# Import shelve for persistent storage and uuid for generating unique IDs
import shelve  # Persistent dictionary-like storage
import uuid  # For generating unique IDs

# Create a Flask application instance
app = Flask(__name__)  # Initialize the Flask application instance
# Set a secret key for securely signing the session cookie
app.secret_key = 'secret_key'  # Secret key for session management and flash messages

# Define the main route for the gig application
@app.route('/')  # Define a route for the root URL
def gig_main():
    # Render the main gig page template
    return render_template('gig_main.html')  # Render the HTML template for the main page

# Define a route to display the gig signup form
@app.route('/gig_signup')  # Define a route for the gig signup form
def gig_form():
    # Render the gig signup form template with no pre-filled applicant data
    return render_template('gig_signup.html', applicant=None)  # Pass `None` to ensure no pre-filled data

# Define a route to add a new applicant, accepting only POST requests
@app.route('/add', methods=['POST'])  # Define a POST route for adding applicants
def add_applicant():
    with shelve.open('applicants.db', writeback=True) as db:  # Open the shelve database in writeback mode
        # Generate a unique ID for the applicant
        applicant_id = str(uuid.uuid4())  # Create a unique identifier for the applicant
        # Save the applicant data to the database
        db[applicant_id] = {  # Store applicant details in a dictionary
            'id': applicant_id,  # Save the unique ID
            'first_name': request.form['first_name'],  # Get the first name from the form
            'last_name': request.form['last_name'],  # Get the last name from the form
            'birth_date': request.form['birth_date'],  # Get the birth date from the form
            'gender': request.form['gender'],  # Get the gender from the form
            'email': request.form['email'],  # Get the email address from the form
            'username': request.form['username'],  # Get the username from the form
            'phone': request.form['phone'],  # Get the phone number from the form
            'city': request.form['city'],  # Get the city from the form
            'state': request.form['state'],  # Get the state from the form
            'zip': request.form['zip'],  # Get the zip code from the form
            'country': request.form['country']  # Get the country from the form
        }
    # Display a success message
    flash('Application added successfully!')  # Notify the user that the application was added
    # Redirect to the view applicants page
    return redirect(url_for('view_applicants'))  # Redirect to the 'view_applicants' route

# Define a route to view all applicants
@app.route('/applicants')  # Define a route to display all applicants
def view_applicants():
    with shelve.open('applicants.db') as db:  # Open the shelve database in read mode
        # Retrieve all applicants as a list of values
        applicants = list(db.values())  # Convert the shelve database values into a list
    # Render the template to display all applicants, passing the applicant list
    return render_template('view_applicants.html', applicants=applicants)  # Pass the list of applicants to the template

# Define a route to edit an applicant's data, accepting both GET and POST requests
@app.route('/edit/<applicant_id>', methods=['GET', 'POST'])  # Define a route to edit an applicant by ID
def edit_applicant(applicant_id):
    with shelve.open('applicants.db', writeback=True) as db:  # Open the shelve database in writeback mode
        # Retrieve the applicant data by ID
        applicant = db[applicant_id]  # Fetch the specific applicant record
        if request.method == 'POST':  # Check if the form was submitted via POST
            # Update the applicant data with the new form values
            applicant.update({  # Use the form data to update the applicant record
                'first_name': request.form['first_name'],  # Update the first name
                'last_name': request.form['last_name'],  # Update the last name
                'birth_date': request.form['birth_date'],  # Update the birth date
                'gender': request.form['gender'],  # Update the gender
                'email': request.form['email'],  # Update the email address
                'username': request.form['username'],  # Update the username
                'phone': request.form['phone'],  # Update the phone number
                'city': request.form['city'],  # Update the city
                'state': request.form['state'],  # Update the state
                'zip': request.form['zip'],  # Update the zip code
                'country': request.form['country']  # Update the country
            })
            # Display a success message
            flash('Application updated successfully!')  # Notify the user that the update was successful
            # Redirect to the view applicants page
            return redirect(url_for('view_applicants'))  # Redirect to the 'view_applicants' route
    # Render the gig signup form template with the current applicant data pre-filled
    return render_template('gig_signup.html', applicant=applicant)  # Pre-fill the form with existing data

# Define a route to delete an applicant by ID
@app.route('/delete/<applicant_id>')  # Define a route to delete an applicant
def delete_applicant(applicant_id):
    with shelve.open('applicants.db', writeback=True) as db:  # Open the shelve database in writeback mode
        # Delete the applicant data from the database
        del db[applicant_id]  # Remove the record corresponding to the given ID
    # Display a success message
    flash('Application deleted successfully!')  # Notify the user that the record was deleted
    # Redirect to the view applicants page
    return redirect(url_for('view_applicants'))  # Redirect to the 'view_applicants' route


# Run the Flask application in debug mode when the script is executed directly
if __name__ == '__main__':  # Check if the script is run directly
    app.run(debug=True)  # Run the Flask application in debug mode
