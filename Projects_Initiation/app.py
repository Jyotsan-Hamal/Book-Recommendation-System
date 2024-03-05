from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import numpy as np
import sqlite3
from flask import g

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key for security

dashboard_df = pickle.load(open('./pickle_files/dashboard.pkl', 'rb'))
data_df = pickle.load(open('./pickle_files/data_df.pkl', 'rb'))
pivot_table = pickle.load(open('./pickle_files/pivot_table.pkl', 'rb'))
similarity = pickle.load(open('./pickle_files/similarity.pkl', 'rb'))

# Dummy user database (replace this with a proper database)
# Connect to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT, name TEXT, email TEXT, address TEXT)''')
conn.commit()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))  # Redirect to the dashboard if the user is logged in
    else:
        return redirect(url_for('login'))  # Redirect to the login page if the user is not logged in


users = {}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('users.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'GET':
            # Fetch the user's data from the database
            username = session['username']
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user_data = c.fetchone()
            c.close()

            if user_data:
                # Load the dashboard data
                dashboard_data = pickle.load(open('./pickle_files/dashboard.pkl', 'rb'))

                return render_template('index.html', user_data=user_data, dashboard_data=dashboard_data)
            else:
                # Handle case where user data is not found
                return "User data not found. Please try again later."

        elif request.method == 'POST':
            # Handle POST method if needed
            # Add logic to process form submissions if applicable
            pass
    else:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        # Get the SQLite connection
        conn = get_db()
        c = conn.cursor()

        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            return "Username already exists! Please choose a different username."

        # Add new user to the database
        c.execute("INSERT INTO users (username, password, name, email, address) VALUES (?, ?, ?, ?, ?)",
                  (username, password, name, email, address))
        conn.commit()

        # Close the cursor
        c.close()

        # Redirect to login page after successful signup
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Get the SQLite connection
        conn = get_db()
        c = conn.cursor()

        # Check if username exists in the database
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user:
            # Retrieve the stored password for the username
            stored_password = user[1]  # Assuming password is stored in the second column

            # Check if the provided password matches the stored password
            if password == stored_password:
                # Add username to session
                session['username'] = username
                return redirect(url_for('index'))

        # Close the cursor
        c.close()

        # If username doesn't exist or password is incorrect, show error message
        return "Invalid username or password. Please try again."

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/recommendation/input', methods=['GET', 'POST'])
def recommendation_input():
    if request.method == 'POST':
        book_name = request.form['book_name']
        return redirect(url_for('recommendation', book_name=book_name))
    
    return render_template('recommendation_input.html')
@app.route('/get_suggestions/<input>', methods=['GET'])
def get_suggestions(input):
    # Get book name suggestions based on user input
    suggestions = [book_name for book_name in data_df['Book-Title'] if input.lower() in book_name.lower()]
    return '<ul>' + ''.join([f'<li>{suggestion}</li>' for suggestion in suggestions]) + '</ul>'

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    if request.method == 'GET':
        return render_template('recommendation_input.html')
    elif request.method == 'POST':
        book_name = request.form['book_name']
        if book_name:
            books, image_urls = recommend(book_name)
            if books:
                zipped_data = zip(books, image_urls)
                return render_template('recommendation.html', zipped_data=zipped_data)
            else:
                return render_template('recommendation.html', message="No recommendations found for the provided book.")
        else:
            return "No book name provided."

def recommend(book_name):
    try:
        index_position = np.where(pivot_table.index==book_name)[0][0]
    
        similarity_scores_ = similarity[index_position]
        
        similarity_scores_with_indexes = list(enumerate(similarity_scores_))
        reverse_sorted_similarity_scores_with_indexes = sorted(similarity_scores_with_indexes,reverse=True,key=lambda x:x[1])
        top5_books = reverse_sorted_similarity_scores_with_indexes[0:6]
    
        book_name_suggestion = []
        book_image_url = []
        for i in top5_books:
            data = data_df[data_df['Book-Title']==pivot_table.index[i[0]]][['Book-Title','Book-Author','Publisher','Image-URL-M']]
            if not data.empty:
                book_image_url.append(data['Image-URL-M'].values[0])
                
                book_name_suggestion.append(pivot_table.index[i[0]])
        
        return book_name_suggestion, book_image_url
    except:
        return False, False

if __name__ == '__main__':
    app.run(debug=True)
