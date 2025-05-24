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

* Register ![Register](https://github.com/user-attachments/assets/f85370ca-3443-4693-9f52-4d670a7ce2bc)
* Login ![Login](https://github.com/user-attachments/assets/62f746c3-8dc1-492b-a603-4d62c12a520d)
* Dashboard with Filter ![Dashboard with Filter](https://github.com/user-attachments/assets/54caf3e8-a1c1-4112-84c8-db819ce3a1dd)
* Dashboard Typing ![Dashboard Typing](https://github.com/user-attachments/assets/c064da47-77bc-4ec5-af97-3072921b8670)
* Dashboard Task Added ![Dashboard Task Added](https://github.com/user-attachments/assets/ae21fbb3-0ca0-41ca-8a95-281342fe4ace)
* Admin Login ![Admin Login](https://github.com/user-attachments/assets/24000a96-f568-4d8c-89c3-2680ff05934a)
* Admin Dashboard ![Admin Dashboard](https://github.com/user-attachments/assets/05c14821-51dd-439a-a5c2-c96f2b7425ad)
* User Tasks ![User Tasks](https://github.com/user-attachments/assets/69f75d51-2fec-48dc-ac8d-abe5d6223b2a)
* Database - logs ![Database - logs](https://github.com/user-attachments/assets/bd54feef-b99f-4227-85b0-c31b12b182be)
* Database - Users ![Database - Users](https://github.com/user-attachments/assets/d2d9676b-c31f-4d88-a7ff-6f848dd2a1c9)
* Database - Tasks ![Database - Tasks](https://github.com/user-attachments/assets/230a0e55-0dac-4eb8-a935-61abbe9a65c0)

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
