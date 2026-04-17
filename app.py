from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import subprocess
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    tasks = db.relationship('Task', backref='assigned_to_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    completed = db.Column(db.Boolean, default=False)



def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("Admin access required.")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for('register'))

        is_first_user = (User.query.count() == 0)

        user = User(
            username=username,
            is_admin=is_first_user
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        if is_first_user:
            flash("First user registered — automatically granted ADMIN privileges.")
        else:
            flash("User registered successfully.")

        return redirect(url_for('login'))

    return render_template('register.html', title="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Logged in.")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html', title="Login")


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('login'))



@app.route('/')
@login_required
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', user=user, title="Dashboard")


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    user = get_current_user()

    if request.method == 'POST':
        receiver_id = int(request.form['receiver_id'])
        content = request.form['content'].strip()

        if receiver_id == user.id:
            flash("You cannot send a message to yourself.")
            return redirect(url_for('messages'))

        receiver = User.query.get(receiver_id)
        if not receiver:
            flash("Receiver not found.")
            return redirect(url_for('messages'))

        msg = Message(sender_id=user.id, receiver_id=receiver_id, content=content)
        db.session.add(msg)
        db.session.commit()
        flash("Message sent.")
        return redirect(url_for('messages'))

    if user.is_admin:
        msgs = Message.query.order_by(Message.timestamp.desc()).all()
    else:
        msgs = Message.query.filter(
            (Message.sender_id == user.id) | (Message.receiver_id == user.id)
        ).order_by(Message.timestamp.desc()).all()

    users = User.query.all()
    return render_template('messages.html', user=user, messages=msgs, users=users, title="Messages")



@app.route('/tasks')
@login_required
def tasks():
    user = get_current_user()
    if user.is_admin:
        all_tasks = Task.query.all()
    else:
        all_tasks = Task.query.filter_by(assigned_to=user.id).all()
    users = User.query.all()
    return render_template('tasks.html', user=user, tasks=all_tasks, users=users, title="Tasks")


@app.route('/tasks/create', methods=['GET', 'POST'])
@admin_required
def create_task():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        assigned_to = request.form.get('assigned_to')
        assigned_to_id = int(assigned_to) if assigned_to else None

        task = Task(title=title, description=description, assigned_to=assigned_to_id)
        db.session.add(task)
        db.session.commit()
        flash("Task created.")
        return redirect(url_for('tasks'))

    users = User.query.all()
    return render_template('create_task.html', users=users, title="Create Task")


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        task.title = request.form['title'].strip()
        task.description = request.form['description'].strip()
        assigned_to = request.form.get('assigned_to')
        task.assigned_to = int(assigned_to) if assigned_to else None
        task.completed = 'completed' in request.form
        db.session.commit()
        flash("Task updated.")
        return redirect(url_for('tasks'))

    users = User.query.all()
    return render_template('edit_task.html', task=task, users=users, title="Edit Task")


@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    user = get_current_user()
    task = Task.query.get_or_404(task_id)

    if not user.is_admin and task.assigned_to != user.id:
        flash("You are not allowed to complete this task.")
        return redirect(url_for('tasks'))

    task.completed = True
    db.session.commit()
    flash("Task marked as completed.")
    return redirect(url_for('tasks'))



@app.route('/admin/python', methods=['GET', 'POST'])
@admin_required
def admin_python_console():
    output = ""
    if request.method == 'POST':
        code = request.form['code']
        try:
            local_vars = {}
            exec(code, globals(), local_vars)
            output = str(local_vars) if local_vars else "Executed."
        except Exception:
            output = traceback.format_exc()

    return render_template('admin_python.html', output=output, title="Admin Python Console")


@app.route('/admin/terminal', methods=['GET', 'POST'])
@admin_required
def admin_terminal():
    output = ""
    if request.method == 'POST':
        cmd = request.form['cmd']
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)

    return render_template('admin_terminal.html', output=output, title="Admin Terminal")



@app.route('/console/python', methods=['GET', 'POST'])
@login_required
def user_python_console():
    output = ""
    if request.method == 'POST':
        code = request.form['code']
        try:
            local_vars = {}
            exec(code, {}, local_vars)
            output = str(local_vars) if local_vars else "Executed."
        except Exception:
            output = traceback.format_exc()

    return render_template('user_python.html', output=output, title="User Python Console")


@app.route('/console/terminal', methods=['GET', 'POST'])
@login_required
def user_terminal():
    output = ""
    if request.method == 'POST':
        cmd = request.form['cmd']
        blocked = ["rm", "del", "shutdown", "reboot", "format", "mkfs", "poweroff"]
        if any(b in cmd.lower() for b in blocked):
            output = "Command blocked."
        else:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
            except Exception as e:
                output = str(e)

    return render_template('user_terminal.html', output=output, title="User Terminal")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
