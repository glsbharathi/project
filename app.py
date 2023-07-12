from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

db= sqlite3.connect('complaints.db')
cursor = db.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    complaint TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved INTEGER DEFAULT 0,
    solution TEXT,
    complaint_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''
cursor.execute(create_table_query)

db.commit()
cursor.close()
db.close()



@app.route('/')
def index():
    db= sqlite3.connect('complaints.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    cursor.close()
    return render_template('index.html', complaints=complaints, logged_in=('username' in session))


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        details = request.form
        name = details['name']
        complaint = details['complaint']
        db= sqlite3.connect('complaints.db')
        cursor = db.cursor()
        sql = "INSERT INTO complaints (name, complaint, complaint_time) VALUES (?, ?, ?)"
        values = (name, complaint, datetime.now())
        cursor.execute(sql, values)
        db.commit()
        cursor.close()
        return 'Complaint submitted successfully'


@app.route('/resolve/<int:complaint_id>', methods=['GET', 'POST'])
def resolve(complaint_id):
    if 'username' in session:
        if request.method == 'POST':
            solution = request.form['solution']
            db= sqlite3.connect('complaints.db')
            cursor = db.cursor()
            sql = "UPDATE complaints SET resolved = 1, solution = ?, resolved_time = ? WHERE id = ?"
            values = (solution, datetime.now(), complaint_id)
            cursor.execute(sql, values)
            db.commit()
            cursor.close()
            return redirect(url_for('admin'))
        else:
            db= sqlite3.connect('complaints.db')
            cursor = db.cursor()
            sql = "SELECT * FROM complaints WHERE id = ?"
            values = (complaint_id,)
            cursor.execute(sql, values)
            complaint = cursor.fetchone()
            cursor.close()
            return render_template('resolve.html', complaint=complaint)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # You can replace this simple authentication with your own logic
        if username == 'admin' and password == 'admin123':
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    if 'username' in session and session['username'] == 'admin':
        db= sqlite3.connect('complaints.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()
        cursor.close()

        # Add the current time to the resolved complaints
        for complaint in complaints:
            if complaint[4]:  # Check if complaint is resolved
                complaint_time = complaint[3]
                resolved_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                complaint += (resolved_time,)  # Add resolved time to the complaint tuple

        return render_template('admin.html', complaints=complaints)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

