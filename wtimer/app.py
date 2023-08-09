import pymysql
import threading
from flask import Flask, render_template, request ,redirect, url_for

app = Flask(__name__)

# Configure MySQL database connection
db = pymysql.connect(
    host="localhost",
    user="root",
    password="sochosocho",
    database="washroom_status",
    cursorclass=pymysql.cursors.DictCursor
)

# Function to create the database and table
def create_database():
    with db.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS washroom_status")
        cursor.execute("USE washroom_status")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_entries (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                minutes INT NOT NULL
            )
        """)
        db.commit()
        print("Database 'washroom_status' and table 'status_entries' have been created.")

# Function to store status entry in the database
def store_status(name, minutes):
    with db.cursor() as cursor:
        sql = "INSERT into status_entries (id, name, minutes) VALUES (1, %s, %s)"
        data = (name, minutes)
        cursor.execute(sql, data)
        db.commit()

# Function to delete status entry from the database
def delete_status_entry(entry_id):
    with db.cursor() as cursor:
        sql = "DELETE FROM status_entries WHERE id = %s"
        cursor.execute(sql, (entry_id,))
        db.commit()

# Function to handle entry deletion after completing the minutes
def delete_entry_after_minutes(entry_id, minutes):
    seconds = minutes * 60
    timer = threading.Timer(seconds, delete_status_entry, args=(entry_id,))
    timer.start()

# Function to retrieve the status entry by ID from the database
def get_status_by_id(entry_id):
    with db.cursor() as cursor:
        sql = "SELECT * FROM status_entries WHERE id = %s"
        cursor.execute(sql, (entry_id,))
        status_entry = cursor.fetchone()
        return status_entry

# Function to retrieve the latest status from the database
def get_latest_status():
    return get_status_by_id(1)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        minutes = int(request.form['minutes'])

        store_status(name, minutes)
        delete_entry_after_minutes(1, minutes)

        return redirect(url_for('popup', name=name, minutes=minutes))
    else:
        latest_status = get_latest_status()
        if latest_status:
            name = latest_status.get('name')
            minutes = latest_status.get('minutes')
            return render_template('popup.html', name=name, minutes=minutes)
        else:
            return render_template('index.html')

@app.route('/popup')
def popup():
    latest_status = get_latest_status()
    if latest_status:
        name = latest_status.get('name')
        minutes = latest_status.get('minutes')
        delete_entry_after_minutes(1, minutes)
        return render_template('popup.html', name=name, minutes=minutes)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    create_database()
    app.run(debug=True)





   
