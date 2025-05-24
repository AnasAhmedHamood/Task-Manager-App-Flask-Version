from flask import Flask, request, render_template_string, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(24)

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

def log_action(user_id, action):
    cursor.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s)", (user_id, action))
    db.commit()
    
@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
            return redirect('/login')
        except mysql.connector.errors.IntegrityError:
            message = "Username already exists."
    return render_template_string(register_html, message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        cursor.execute("SELECT * FROM users WHERE name = %s", (uname,))
        user = cursor.fetchone()
        if user and check_password_hash(user[3], pwd):
            session['user'] = uname
            session['user_id'] = user[0]
            log_action(user[0], "Logged in")
            if user[5]:
                return redirect('/admin')
            return redirect('/dashboard')
        else:
            message = "Invalid username or password."
    return render_template_string(login_html, message=message)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    uname = session['user']
    cursor.execute("SELECT id FROM users WHERE name = %s", (uname,))
    result = cursor.fetchone()
    if not result:
        return redirect('/login')
    user_id = result[0]

    filter_type = request.args.get('filter', 'all')
    if filter_type == 'completed':
        cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s AND completed = 1", (user_id,))
    elif filter_type == 'pending':
        cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s AND completed = 0", (user_id,))
    else:
        cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s", (user_id,))

    tasks = [{'id': row[0], 'task': row[1], 'completed': row[2]} for row in cursor.fetchall()]
    return render_template_string(home_html, tasks=tasks, user=uname)

@app.route('/add-task', methods=['POST'])
def add_task():
    if 'user' not in session:
        return redirect('/login')
    uname = session['user']
    cursor.execute("SELECT id FROM users WHERE name = %s", (uname,))
    result = cursor.fetchone()
    if not result:
        return redirect('/login')
    user_id = result[0]
    task = request.form.get('task')
    if task:
        cursor.execute("INSERT INTO todos (user_id, task, completed) VALUES (%s, %s, %s)", (user_id, task, False))
        db.commit()
        log_action(user_id, "Added task")
    return redirect('/dashboard')

@app.route('/remove-task', methods=['POST'])
def remove_task():
    if 'user' not in session:
        return redirect('/login')

    uname = session['user']
    cursor.execute("SELECT id FROM users WHERE name = %s", (uname,))
    result = cursor.fetchone()
    user_id = result[0]

    task_id = request.form.get('task_id')
    if task_id:
        cursor.execute("DELETE FROM todos WHERE id = %s", (task_id,))
        db.commit()
        log_action(user_id, f"Removed task ID {task_id}")
    return redirect('/dashboard')


@app.route('/toggle-task', methods=['POST'])
def toggle_task():
    if 'user' not in session:
        return redirect('/login')
    task_id = request.form.get('task_id')
    new_status = request.form.get('completed')
    if task_id and new_status is not None:
        cursor.execute("UPDATE todos SET completed = %s WHERE id = %s", (new_status, task_id))
        db.commit()
        action = "Marked task as complete" if new_status == "1" else "Marked task as incomplete"
        log_action(session['user_id'], action)
    return redirect('/dashboard')


@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')

    base_query = "SELECT id, name, email, is_verified FROM users WHERE is_admin = 0"
    filters = []
    params = []

    if search:
        filters.append("(name LIKE %s OR email LIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if status == "verified":
        filters.append("is_verified = 1")
    elif status == "unverified":
        filters.append("is_verified = 0")

    if filters:
        base_query += " AND " + " AND ".join(filters)

    base_query += " ORDER BY id DESC"
    cursor.execute(base_query, params)
    users = cursor.fetchall()

    return render_template_string(admin_html, users=users, search=search, status=status)


@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session:
        return redirect('/login')
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return redirect('/admin')

@app.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        log_action(session['user_id'], "Logged out")
    session.clear()
    return redirect('/login')


# HTML Templates
login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Login | Task Manager</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: #ffffff;
      padding: 40px;
      border-radius: 16px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.15);
      max-width: 420px;
      width: 100%;
    }
    h2 {
      text-align: center;
      margin-bottom: 24px;
      color: #333;
      font-weight: 600;
    }
    form {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    input[type="text"], input[type="password"] {
      padding: 12px 16px;
      font-size: 15px;
      border: 1px solid #ccc;
      border-radius: 8px;
      transition: border-color 0.3s ease;
    }
    input:focus {
      border-color: #4e4376;
      outline: none;
    }
    button {
      padding: 12px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      border: none;
      border-radius: 8px;
      color: white;
      font-weight: 600;
      font-size: 16px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    button:hover {
      transform: translateY(-2px);
    }
    .error {
      color: #d93025;
      background: #fce8e6;
      padding: 10px;
      border-radius: 6px;
      font-size: 14px;
      text-align: center;
    }
    .link {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
    }
    .link a {
      color: #4e4376;
      text-decoration: none;
      font-weight: 500;
    }
    .link a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Login to Your Account</h2>
    {% if message %}<div class="error">{{ message }}</div>{% endif %}
    <form method="POST" action="/login">
      <input type="text" name="username" placeholder="Username" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <div class="link">
      <p>Don't have an account? <a href="/register">Register here</a></p>
    </div>
  </div>
</body>
</html>

"""
register_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Register | Task Manager</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: #ffffff;
      padding: 40px;
      border-radius: 16px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.15);
      max-width: 420px;
      width: 100%;
    }
    h2 {
      text-align: center;
      margin-bottom: 24px;
      color: #333;
      font-weight: 600;
    }
    form {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    input[type="text"], input[type="email"], input[type="password"] {
      padding: 12px 16px;
      font-size: 15px;
      border: 1px solid #ccc;
      border-radius: 8px;
      transition: border-color 0.3s ease;
    }
    input:focus {
      border-color: #4e4376;
      outline: none;
    }
    button {
      padding: 12px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      border: none;
      border-radius: 8px;
      color: white;
      font-weight: 600;
      font-size: 16px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    button:hover {
      transform: translateY(-2px);
    }
    .error {
      color: #d93025;
      background: #fce8e6;
      padding: 10px;
      border-radius: 6px;
      font-size: 14px;
      text-align: center;
    }
    .link {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
    }
    .link a {
      color: #4e4376;
      text-decoration: none;
      font-weight: 500;
    }
    .link a:hover {
      text-decoration: underline;
    }
    .note {
      font-size: 12px;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Create Your Account</h2>
    {% if message %}<div class="error">{{ message }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required />
      <input type="email" name="email" placeholder="Email address" required />
      <input type="password" name="password" placeholder="Password" required />
      <span class="note">Password must be at least 8 characters</span>
      <button type="submit">Register</button>
    </form>
    <div class="link">
      <p>Already have an account? <a href="/login">Login here</a></p>
    </div>
  </div>
</body>
</html>
"""
home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>User Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }
    .dashboard {
      max-width: 800px;
      margin: 0 auto;
      background: #ffffff;
      padding: 30px;
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    h2 {
      text-align: center;
      margin-bottom: 30px;
      color: #4e4376;
    }
    .task-form, .filter-form {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }
    input[type="text"], select {
      flex: 1;
      padding: 12px;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 15px;
    }
    button {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      padding: 12px 20px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s ease;
    }
    button:hover {
      opacity: 0.95;
    }
    ul {
      list-style: none;
      padding: 0;
    }
    li {
      background: #f7f7f7;
      padding: 12px 20px;
      border-radius: 8px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .task-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .task-text {
      font-weight: 500;
      color: #333;
    }
    .task-completed {
      text-decoration: line-through;
      color: #aaa;
    }
    .task-actions {
      display: flex;
      gap: 10px;
    }
    .remove-btn, .edit-btn {
      background: none;
      border: none;
      font-weight: bold;
      cursor: pointer;
      font-size: 16px;
    }
    .remove-btn {
      color: #d93025;
    }
    .edit-btn {
      color: #007bff;
    }
    .logout-btn {
      display: block;
      margin: 30px auto 0;
      background: #dc3545;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
    }
    .logout-btn:hover {
      background: #c82333;
    }
  </style>
</head>
<body>
  <div class="dashboard">
    <h2>Welcome, {{ user }}</h2>

    <!-- Add Task Form -->
    <form class="task-form" method="POST" action="/add-task">
      <input type="text" name="task" placeholder="Enter a new task..." required>
      <button type="submit">Add Task</button>
    </form>

    <!-- Filter Form -->
    <form class="filter-form" method="GET" action="/dashboard">
      <select name="filter">
        <option value="all" {% if request.args.get('filter') == 'all' %}selected{% endif %}>All Tasks</option>
        <option value="completed" {% if request.args.get('filter') == 'completed' %}selected{% endif %}>Completed</option>
        <option value="pending" {% if request.args.get('filter') == 'pending' %}selected{% endif %}>Pending</option>
      </select>
      <button type="submit">Filter</button>
    </form>

    <!-- Task List -->
    <ul>
      {% for task in tasks %}
      <li>
        <div class="task-info">
          <form method="POST" action="/toggle-task">
            <input type="hidden" name="task_id" value="{{ task.id }}">
            <input type="hidden" name="completed" value="{{ 0 if task.completed else 1 }}">
            <input type="checkbox" onchange="this.form.submit()" {% if task.completed %}checked{% endif %}>
          </form>
          <span class="task-text {% if task.completed %}task-completed{% endif %}">{{ task.task }}</span>
        </div>
        <div class="task-actions">
          <form method="POST" action="/remove-task">
            <input type="hidden" name="task_id" value="{{ task.id }}">
            <button type="submit" class="remove-btn" title="Delete">&times;</button>
          </form>
          <button type="button" class="edit-btn" onclick="alert('Edit functionality coming soon')">Edit</button>
        </div>
      </li>
      {% endfor %}
    </ul>

    <form method="POST" action="/logout">
      <button class="logout-btn">Logout</button>
    </form>
  </div>
</body>
</html>


"""
admin_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Panel | Task Manager</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
      min-height: 100vh;
      padding: 30px;
      color: #333;
    }
    .admin-panel {
      max-width: 1000px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 16px;
      padding: 30px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    h1 {
      text-align: center;
      margin-bottom: 20px;
      color: #4e4376;
    }
    .filter-form {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 20px;
      justify-content: space-between;
    }
    .filter-form input[type="text"],
    .filter-form select {
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid #ccc;
      flex: 1;
      min-width: 220px;
    }
    .filter-form button {
      background: #4e4376;
      color: white;
      padding: 10px 16px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
    }
    .filter-form button:hover {
      background: #3a2f5a;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 14px 16px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }
    th {
      background: #f0f0f0;
      color: #444;
    }
    tr:hover {
      background: #f9f9f9;
    }
    .delete-btn {
      background: #e74c3c;
      color: white;
      padding: 8px 12px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
    }
    .delete-btn:hover {
      background: #c0392b;
    }
    .view-tasks-btn {
      background: #4e4376;
      color: white;
      padding: 8px 12px;
      margin-left: 5px;
      border-radius: 6px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
    }
    .view-tasks-btn:hover {
      background: #372c5f;
    }
    .logout-form {
      margin-top: 30px;
      text-align: center;
    }
    .logout-btn {
      background: #dc3545;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
    }
    .logout-btn:hover {
      background: #c82333;
    }
  </style>
</head>
<body>
  <div class="admin-panel">
    <h1>Admin Dashboard</h1>

    <form method="GET" class="filter-form" action="/admin">
      <input type="text" name="search" placeholder="Search by username or email" value="{{ search or '' }}">
      <select name="status">
        <option value="">All</option>
        <option value="verified" {% if status == 'verified' %}selected{% endif %}>Verified</option>
        <option value="unverified" {% if status == 'unverified' %}selected{% endif %}>Unverified</option>
      </select>
      <button type="submit">Filter</button>
    </form>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
          <th>Verified</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for user in users %}
        <tr>
          <td>{{ user[0] }}</td>
          <td>{{ user[1] }}</td>
          <td>{{ user[2] }}</td>
          <td>{{ 'Yes' if user[3] else 'No' }}</td>
          <td>
            <form method="POST" action="/admin/delete/{{ user[0] }}" style="display:inline;">
              <button class="delete-btn" type="submit">Delete</button>
            </form>
            <a href="/admin/tasks/{{ user[0] }}" class="view-tasks-btn">View Tasks</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <form method="POST" action="/logout" class="logout-form">
      <button type="submit" class="logout-btn">Logout</button>
    </form>
  </div>
</body>
</html>
"""
# task
@app.route('/admin/tasks/<int:user_id>')
def admin_user_tasks(user_id):
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return "User not found", 404

    cursor.execute("SELECT task, completed FROM todos WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()

    task_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{user[0]}'s Tasks</title>
      <style>
        body {{
          background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
          font-family: 'Inter', sans-serif;
          color: white;
          padding: 2rem;
        }}
        .container {{
          background: #1c1e29;
          padding: 30px;
          border-radius: 12px;
          max-width: 600px;
          margin: 0 auto;
        }}
        h2 {{ text-align: center; margin-bottom: 20px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{
          background: #2d3436;
          padding: 10px 15px;
          margin-bottom: 10px;
          border-radius: 6px;
        }}
        .completed {{
          text-decoration: line-through;
          opacity: 0.6;
        }}
        a.back {{
          display: block;
          text-align: center;
          margin-top: 20px;
          color: #00bcd4;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>{user[0]}'s Task List</h2>
        <ul>
          {''.join([f'<li class="{'completed' if t[1] else ''}">{t[0]}</li>' for t in tasks]) or '<p>No tasks found.</p>'}
        </ul>
        <a class="back" href="/admin">&larr; Back to Admin</a>
      </div>
    </body>
    </html>
    """
    return task_html

if __name__ == '__main__':
    app.run(debug=True)
