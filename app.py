import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

# SECURITY SECURITY SECURITY
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Database 
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -atabase Model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(50))
    action = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database Initialization Error: {e}")

# Login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Log in accounts
users = {"admin": generate_password_hash("root")}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None


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
        print(f"Logging Error: {e}")

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and check_password_hash(users["admin"], password):
            user = User(username)
            login_user(user)
            # Log exact clean action notif
            record_activity("LOGIN SUCCESS", username)
            return redirect(url_for('dashboard'))
        else:
            # Log failed attempt notif
            record_activity(f"FAILED LOGIN ATTEMPT: {username}")
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/get_logs')
@login_required
def get_logs():
    try:
        logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(50).all()
        output = ""
        for log in logs:
            # Timestamp with correct utc
            taiwan_time = log.timestamp + timedelta(hours=8)
            time_str = taiwan_time.strftime("%Y-%m-%d %H:%M:%S")
            
            output += f"[{time_str} UTC+8] {log.username} - {log.action} ({log.ip_address})\n"
            
        return output if output else "Awaiting first security event..."
    except Exception as e:
        return f"Database Error: {e}"

@app.route('/dashboard')
@login_required
def dashboard():
    # User activity log 
    record_activity("ACCESSED LIVE CAMERA FEED", current_user.id)
    return render_template('camera.html')

@app.route('/logout')
@login_required
def logout():
    # Log out action
    record_activity("LOGOUT", current_user.id)
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
