import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'soc_exam_secret_key'

# --- 1. Database Configuration ---
# Railway provides the DATABASE_URL automatically in production
app.config['SQLALCHEMY_DATABASE_VALUE'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. Database Models (Your Tables) ---
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))

# Create the tables in the database
with app.app_context():
    db.create_all()

# --- 3. Clean Logging Function ---
def log_event(action, user=None):
    new_log = AuditLog(
        action=action, 
        username=user if user else "System", 
        ip_address=request.remote_addr
    )
    db.session.add(new_log)
    db.session.commit()

# --- 4. Updated Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Using your admin / root credentials
        if username == "admin" and password == "root":
            user = User(username)
            login_user(user)
            log_event("LOGIN SUCCESS", user=username)
            return redirect(url_for('dashboard'))
        else:
            log_event(f"FAILED LOGIN ATTEMPT: {username}")
            flash('Invalid credentials')
    return render_template('login.html')

# --- 5. Updated Log Retrieval ---
@app.route('/get_logs')
@login_required
def get_logs():
    # Query the last 50 logs from the Postgres table
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    
    log_output = ""
    for entry in logs:
        # Format: [Time] USER - ACTION (IP)
        time_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        log_output += f"[{time_str}] {entry.username} - {entry.action} ({entry.ip_address})\n"
    
    return log_output

# ... Keep the rest of your User class and logout routes ...
