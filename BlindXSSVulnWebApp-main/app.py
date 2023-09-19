import hashlib
from flask import Flask, flash, render_template, request, make_response, session, redirect
import os
import sqlite3


app = Flask(__name__)

con = sqlite3.connect('users.db',check_same_thread=False)
x = con.cursor()
x.execute('''CREATE TABLE IF NOT EXISTS comments
             (comment_text TEXT)''')
def insert_comment(text):
    x.execute("INSERT INTO comments (comment_text) VALUES (?)", (text,))
    con.commit()

def delete_all_comments():
    try:
        x.execute("DELETE FROM comments")
        con.commit()
        return True
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('index.html',text = session.get('admin_logged_in'))

@app.route('/thankyou', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        message = request.form['message']
        insert_comment(message) 
        return render_template('thankyou.html', message=message)
    else:
        response = make_response(render_template('message.html'))
        return response

def check_password(username, password, con):
    # Get the user's salt and password hash from the database
    cur = con.cursor()
    cur.execute("SELECT salt, password_hash FROM users WHERE username=?", (username,))
    result = cur.fetchone()

    if result is not None:
        salt = result[0]
        password_hash = result[1]

        # Hash the password with the salt using SHA-256
        test_password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

        # Compare the hash with the one in the database
        if test_password_hash == password_hash:
            return True

    return False
@app.route('/login', methods=['POST'])
def do_admin_login():
    password = request.form['psw']
    user = request.form['id']
    con = sqlite3.connect('users.db')
    if check_password(user, password, con):
        session['logged_in'] = True
        session['username'] = user
        if user == 'admin':  # Set the user to 'admin' in the session
            session['admin_logged_in'] = True
        else:
            session.pop('user', None)  # Clear the user session variable
            session['admin_logged_in'] = False
    else:
        flash('wrong password!')
    return home()


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Clear the logged_in session variable
    return redirect('/')

@app.route('/comments')
def show_comments():
    # Query the database to retrieve all comments
    x.execute("SELECT comment_text FROM comments")
    comments = x.fetchall()

    return render_template('comments.html', comments=comments)

@app.route('/delete_comments', methods=['POST'])
def delete_comments():
    # Check if the user is an admin
    if session.get('admin_logged_in'):
        # Call the delete_all_comments function to delete all comments
        if delete_all_comments():
            flash('All comments deleted successfully.')
        else:
            flash('Failed to delete comments.')

    # Redirect back home
    return redirect('/')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0')