import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'soc_exam_secret_key'

# --- 1. Database Configuration ---
# This looks for the variable you set in Railway
db_url = os.environ.get('DATABASE_URL')

# Troubleshooting: This helps us see if the variable is missing in the Railway logs
if not db_url:
    print("CRITICAL: DATABASE_URL not found in environment variables!")
else:
    # SQLAlchemy requires 'postgresql://', but Supabase often gives 'postgres://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. Database Model ---
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(50))
    action = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))

# Automatically create the table in Supabase on startup
with app.app_context():
    try:
        db.create_all()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Database error: {e}")

# --- 3. Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Credentials: admin / root
users = {"admin": generate_password_hash("root")}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

# --- 4. Audit Logging Function ---
def record_activity(action, username="System"):
    try:
        new_entry = AuditLog(
            username=username,
            action=action,
            ip_address=request.remote_addr
        )
        db.session.add(new_entry)
        db.session.commit()
    except Exception as e:
        print(f"Logging failed: {e}")

# --- 5. Routes ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users["admin"], password):
            user = User(username)
            login_user(user)
            record_activity("LOGIN SUCCESS", username)
            return redirect(url_for('dashboard'))
        else:
            record_activity(f"FAILED LOGIN ATTEMPT: {username}")
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/get_logs')
@login_required
def get_logs():
    try:
        # Pull latest 20 events from PostgreSQL
        logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(20).all()
        output = ""
        for log in logs:
            time_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            output += f"[{time_str}] {log.username} - {log.action} ({log.ip_address})\n"
        return output if output else "Awaiting first security event..."
    except Exception as e:
        return f"Error retrieving logs from database: {str(e)}"

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('camera.html')

@app.route('/logout')
@login_required
def logout():
    record_activity("LOGOUT", current_user.id)
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
