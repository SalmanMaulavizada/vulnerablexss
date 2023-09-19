import sqlite3
import hashlib
import uuid

# Create a connection to the SQLite database
conn = sqlite3.connect('users.db',check_same_thread=False)

# Create a cursor object to execute SQL commands
c = conn.cursor()

# Create the users table if it doesn't already exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT, password TEXT)''')


def delete_all_comments():
    try:
        c.execute("DELETE FROM comments")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False

def create_user(username, password):
    # Insert the user into the database
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password))
    conn.commit()

def check_password(username, password):
    # Get the user's salt and password hash from the database
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result is not None:
     return True
    else:
     return False

# Example usage
create_user('hacker', 'password123')
create_user('admin', 'password456')

print(check_password('hacker', 'password123')) # True
print(check_password('admin', 'wrongpassword')) # False