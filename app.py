import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_exam_key' 

# --- 1. Set up Intrusion Logging ---
# Captures failed attempts in security.log (viewable in Railway "View Logs")
logging.basicConfig(filename='security.log', level=logging.WARNING, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. Set up Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin Account Credentials
users = {
    "admin": generate_password_hash("password123") 
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# --- 3. Routes ---
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        client_ip = request.remote_addr

        if username in users and check_password_hash(users.get(username), password):
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            # HONEYPOT LOG: This is what your professor needs to see in the logs!
            logging.warning(f"INTRUSION ALERT: Failed login attempt from IP: {client_ip} using username: {username}")
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('camera.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Railway assigns a port automatically via environment variables
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
