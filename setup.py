import os, webbrowser, subprocess, sys
from threading import Timer

from app import app, db
with app.app_context():
    db.create_all()

subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask_sqlalchemy", "werkzeug"])
home = os.path.expanduser("~")
app_path = os.path.join(home, "Downloads", "creat_prog", "app.py")
if os.path.isfile(app_path):
    subprocess.Popen([sys.executable, app_path])
    Timer(1.5, webbrowser.open, args=["http://127.0.0.1:5000"]).start()
else:
    print("app.py not found:", app_path)
