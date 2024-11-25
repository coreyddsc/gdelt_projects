import dash
from dash import dcc, html, Output, Input
import yaml
import bcrypt
from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
# from flask_dance.contrib.microsoft import make_microsoft_blueprint, microsoft

# Hash function
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def handle_login(app):
    # Load config
    with open("configs/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Check and hash passwords if necessary
    for username, details in config['credentials']['usernames'].items():
        # If password is not already hashed (it should not start with '$2b$' if it's plaintext)
        if not details['password'].startswith('$2b$'):
            print(f"Hashing password for {username}")
            details['password'] = hash_password(details['password'])
            
    # Save updated config back to the file
    with open("configs/config.yaml", "w") as file:
        yaml.dump(config, file)

    # print("Updated config with hashed passwords:")
    # print(config)

    # User database (from config.yaml)
    users_db = config['credentials']['usernames']
    app.server.users = {}

    # Create User class for flask_login
    class User(UserMixin):
        def __init__(self, username, email, roles, logged_in, password=None):
            self.id = username
            self.email = email
            self.roles = roles
            self.logged_in = logged_in
            self.password = password  # Add the password field here

        def is_authenticated(self):
            return self.logged_in

    # Load users from the config into the users dictionary
    for username, details in users_db.items():
        password = details["password"]  # The hashed password from config.yaml
        app.server.users[username] = User(username, details["email"], details["roles"], details["logged_in"], password)

    return app.server.users


def access_flask_server(app):
    # server = app.server  # Access the underlying Flask server

    # Set the app secret key from the configuration
    with open("configs/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    app.server.secret_key = config["cookie"]["key"]

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app.server)

    # Initialize the users dictionary by calling the handle_login function from the component
    users = handle_login(app)

    # Define the root route
    @app.server.route('/')
    def index():
        return redirect('/login')  # Redirect to login page

    # Set the login view for Flask-Login
    login_manager.login_view = 'login'

    # Setup the login manager to load the user
    @login_manager.user_loader
    def load_user(user_id):
        return users.get(user_id)

    # Set up the logout route in the app
    @app.server.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect('/')

def register_user(app):
    # Add user registration route
    @app.server.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            hashed_password = hash_password(password)

            # Add user to config.yaml (you may also use a database instead)
            with open("configs/config.yaml", "r") as file:
                config = yaml.safe_load(file)
            
            config['credentials']['usernames'][username] = {
                "email": email,
                "roles": ["user"], # Default role
                "logged_in": False,
                "password": hashed_password
            }
            
            with open("configs/config.yaml", "w") as file:
                yaml.dump(config, file)

            return redirect('/login')

        return render_template('register.html')  # Render a registration template


# Add Google OAuth route
def add_google_oauth(app):
    google_bp = make_google_blueprint(client_id='your_google_client_id', client_secret='your_google_client_secret', redirect_to='google_login')
    app.server.register_blueprint(google_bp, url_prefix='/google_login')

    @app.server.route('/google_login')
    def google_login():
        if not google.authorized:
            return redirect(url_for('google.login'))

        # Fetch user info from Google
        resp = google.get('/plus/v1/people/me')
        assert resp.ok, resp.text
        user_info = resp.json()
        username = user_info['displayName']

        # Create user if they don't exist in the local system
        user = app.server.users.get(username)
        if not user:
            email = user_info['emails'][0]['value']
            app.server.users[username] = User(username, email, ['user'], True)

        # Log the user in
        user = app.server.users[username]
        login_user(user)
        return redirect('/')  # Redirect to the main page after successful login


def handle_logout(app):
    @app.callback(
        Output('redirect', 'href'),
        [Input('logout', 'n_clicks')]
    )
    def logout_redirect(n_clicks):
        if n_clicks > 0:
            logout_user()
            return "/login"  # Redirect to the login page
        return None


def login_route(app):
    # server = app.server  # Access the underlying Flask server
    @app.server.route('/login', methods=['GET', 'POST'])
    def login():
        error_message = None

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            print(f"Entered password: {password}")  # Debugging print

            # Get user from the users dictionary
            user = app.server.users.get(username)
            app.current_user = user  # Set the user in the app
            if user:
                print(f"Stored hash for {username}: {user.password}")  # Debugging print

                # Check password match
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    print(f"Password match for {username}")  # Debugging print
                    login_user(user)
                    return redirect('/')  # Redirect to a dashboard or main page
                else:
                    print(f"Invalid password for {username}")  # Debugging print
                    error_message = "Invalid username or password."
            else:
                print(f"User {username} not found")  # Debugging print
                error_message = "Invalid username or password."

        return render_template('login.html', error_message=error_message)
