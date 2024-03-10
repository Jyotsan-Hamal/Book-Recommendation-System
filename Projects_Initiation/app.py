from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import numpy as np
import sqlite3
from flask import g
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key for security

# Load pickled data
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

# Define helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

def fetch_user_data(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = c.fetchone()
    c.close()
    return user_data

def load_dashboard_data():
    with open('./pickle_files/dashboard.pkl', 'rb') as file:
        dashboard_data = pickle.load(file)
    return dashboard_data.to_dict(orient='records')

# Routes
@login_required
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@login_required
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'GET':
            username = session['username']
            user_data = fetch_user_data(username)
            if user_data:
                dashboard_data = load_dashboard_data()
                return render_template('index.html', user_data=user_data, dashboard_data=dashboard_data)
            else:
                return "User data not found. Please try again later."
        elif request.method == 'POST':
            # Handle POST method if needed
            pass
    else:
        return redirect(url_for('login'))
    
@login_required
@app.route('/book_details/<book_title>', methods=['GET'])
def book_details(book_title):
    # Fetch data for the selected book from data_df.pkl
    book_data = data_df[data_df['Book-Title'] == book_title]
    if not book_data.empty:
        # Render template with book details
        return render_template('book_details.html', book_data=book_data)
    else:
        return "Book details not found."

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup form submission
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password, name, email, address) VALUES (?, ?, ?, ?, ?)",
                  (username, password, name, email, address))
        conn.commit()
        c.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user:
            stored_password = user[1]

            if password == stored_password:
                session['username'] = username
                return redirect(url_for('index'))

        c.close()

        return "Invalid username or password. Please try again."

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

@login_required
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

@login_required
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

@login_required
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
