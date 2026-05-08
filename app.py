import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_production_key_123')
csrf = CSRFProtect(app)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///system.db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(50))
    action = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))

with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
users = {"admin": generate_password_hash(admin_password)}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

def sanitize_log_input(text):
    return re.sub(r'[\r\n]', '', str(text))

def record_activity(action, username="System"):
    try:
        safe_action = sanitize_log_input(action)
        safe_username = sanitize_log_input(username)
        new_entry = AuditLog(
            username=safe_username, 
            action=safe_action, 
            ip_address=request.remote_addr
        )
        db.session.add(new_entry)
        db.session.commit()
    except Exception:
        pass

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and check_password_hash(users["admin"], password):
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
        logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(20).all()
        output = ""
        for log in logs:
            taiwan_time = log.timestamp + timedelta(hours=8)
            time_str = taiwan_time.strftime("%Y-%m-%d %H:%M:%S")
            output += f"[{time_str} UTC+8] {log.username} - {log.action} ({log.ip_address})\n"
        return output if output else "Awaiting first security event..."
    except Exception:
        return "System unavailable."

@app.route('/dashboard')
@login_required
def dashboard():
    record_activity("ACCESSED LIVE CAMERA FEED", current_user.id)
    return render_template('camera.html')

@app.route('/logout')
@login_required
def logout():
    record_activity("LOGOUT", current_user.id)
    logout_user()
    return redirect(url_for('login'))
