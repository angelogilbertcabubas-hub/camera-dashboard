import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'soc_exam_secret_key'

# --- 1. Audit Logging Logic ---
LOG_FILE = 'audit.log'

def write_audit_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

# --- 2. Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Updated Credentials: admin / root
users = {
    "admin": generate_password_hash("root")
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

# --- 3. Routes ---

@app.route('/')
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
            write_audit_log(f"LOGIN SUCCESS: User '{username}' accessed system from {client_ip}")
            return redirect(url_for('dashboard'))
        else:
            write_audit_log(f"LOGIN ATTEMPT: Failed login for '{username}' from {client_ip}")
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    write_audit_log(f"ACTIVITY: User '{current_user.id}' viewing Live Video Feed")
    return render_template('camera.html')

@app.route('/get_logs')
@login_required
def get_logs():
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                return "".join(lines[-20:]) # Show last 20 clean entries
        return "System Initialized. Awaiting activity..."
    except Exception as e:
        return f"Log Error: {str(e)}"

@app.route('/logout')
@login_required
def logout():
    user_name = current_user.id
    write_audit_log(f"LOGOUT: User '{user_name}' disconnected.")
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
