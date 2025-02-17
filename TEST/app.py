from flask import Flask, render_template
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    database = sqlite3.connect('./Captured_requests.db')
    cursor = database.cursor()
    entries = cursor.execute('SELECT * FROM all_requests ORDER BY Request_Number DESC')
    return render_template("home.html", entries=entries)

@app.route('/intercept.html')
def intercept():
    return render_template("intercept.html")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, port=8001)