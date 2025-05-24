import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

# Delete if exists
cursor.execute("DELETE FROM users WHERE name = %s", ("ADMIN_PASSWORD",))
db.commit()

# Generate hash
hashed = generate_password_hash(os.getenv("ADMIN_PASSWORD", "defaultpassword"), method="scrypt")

# Insert admin again
cursor.execute("""
    INSERT INTO users (name, email, password, is_verified, is_admin)
    VALUES (%s, %s, %s, %s, %s)
""", ("admin.anas", "anas.admin@example.com", hashed, True, True))
db.commit()

print("Admin user reset successfully.")
