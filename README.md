# 🖥️ Flask Admin & User Management System  
A modern, feature‑rich internal web system built with **Flask**, featuring messaging, task management, admin tools, and fully interactive Python/terminal consoles.

This project is designed for **local use only** (e.g., school projects, demos, offline tools).  
It is **not intended for deployment** due to the powerful admin console capabilities.

---

## 🚀 Features

### 👤 User System
- Secure login & logout  
- First registered user becomes **Admin automatically**  
- All later users are **standard users**  
- Admins can elevate users later (if you add a management panel)

---

### 💬 Messaging System
- Users can send messages to other users  
- Users only see:
  - Messages they sent  
  - Messages they received  
- Admins can see **all messages**  
- Clean, modern UI with Bootstrap 5

---

### 📋 Task Management
Admins can:
- Create tasks  
- Edit tasks  
- Assign tasks to users  
- Mark tasks as completed  

Users can:
- View tasks assigned to them  
- Mark their tasks as completed  

---

### 🛠️ Admin Tools (Powerful)
Admins get access to full system‑level tools:

#### 🔥 Admin Python Console
- Executes **real Python code**  
- Full access to variables, imports, and system state  

#### 🔥 Admin Terminal Console
- Executes **real system commands** (cmd, PowerShell, bash)  
- Full stdout/stderr output  

---

### 🧪 User Tools

#### 🐍 User Python Console
- Executes Python code  
- Limited environment  

#### 💻 User Terminal Console
- Executes system commands  
- Dangerous commands blocked  

---

### 🎨 Modern UI
- Sidebar navigation  
- Dashboard cards  
- Bootstrap 5 + Icons  
- Clean, responsive layout  

---

## 📁 Project Structure

```
your_project/
├─ app.py
└─ templates/
   ├─ base.html
   ├─ login.html
   ├─ register.html
   ├─ dashboard.html
   ├─ messages.html
   ├─ tasks.html
   ├─ create_task.html
   ├─ edit_task.html
   ├─ admin_python.html
   ├─ admin_terminal.html
   ├─ user_python.html
   ├─ user_terminal.html
```

---

## 🛠️ Installation & Setup

### 1. Install dependencies
```
pip install flask flask_sqlalchemy werkzeug
```

### 2. Run the app
```
python app.py
```

### 3. Open in browser  
```
http://127.0.0.1:5000/
```

### 4. Register the first user  
The **first account** becomes **Admin automatically**.

---

## ⚠️ Security Warning
This system includes:
- A full Python execution console  
- A full system command console  

These features are **intended ONLY for local/offline use**.  
Do **NOT** deploy this application publicly.

---

## 📚 Technologies Used
- Python 3  
- Flask  
- SQLAlchemy  
- Bootstrap 5  
- HTML / Jinja2 Templates  

---

## 📌 Future Improvements
- Admin user management panel  
- Real‑time chat (WebSockets)  
- File uploads  
- Activity logs  
- Dark mode  
- Analytics dashboard  

