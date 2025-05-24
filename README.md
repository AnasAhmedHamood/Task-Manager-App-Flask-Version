# Task-Manager-App-Flask-Version

A simple task manager built with **Flask** using **MySQL** and **Jinja2** templates.

---

## ✨ Features

- User registration and login
- Secure password hashing
- Session-based authentication
- Add, delete, and toggle task status
- Filter tasks (all, completed, pending)
- Admin dashboard for user management
- Admin can view tasks of any user
- Logs user actions like login/logout/task edits

---

## 🛠 Tech Stack

- **Backend:** Flask  
- **Frontend:** HTML + Jinja2 templates  
- **Database:** MySQL  
- **Authentication:** Flask sessions  
- **Password Security:** Werkzeug  
- **Environment Config:** python-dotenv  

---

## 📸 Screenshots

_Add screenshots here after pushing them:_

- Register ![Register](https://github.com/user-attachments/assets/fc26b91e-0f54-4311-be84-e71ee01a689b)
- ![Login](login.png)
- ![User Dashboard](dashboard.png)
- ![Admin Login](admin_login.png)
- ![Admin Panel](admin_panel.png)
- ![Task View](user_tasks.png)

---

## ⚙️ Setup Before Testing

Before running the app, make sure the following are installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/)
- [Visual Studio Code](https://code.visualstudio.com/)

Ensure MySQL is running and a database is created. Also, configure your `.env` file like this:

```env
SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=your_admin_password
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

---

## 🚀 How to Run (VS Code)

1. Install required Python packages:

```bash
pip install flask mysql-connector-python python-dotenv werkzeug
```

2. Run the Flask app:

```bash
python task-flask.py
```

3. Open your browser and go to:

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```plaintext
.
├── .env
├── hash_pass.py
├── task-flask.py
```

---

## 👨‍💻 Author

**Anas Ahmed Hamood**

---

## 📄 License

This project is licensed under the MIT License.
