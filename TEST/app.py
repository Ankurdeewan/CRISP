import flask 
from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
from proxy_server import forward_request

import threading

intercept_status = False  
intercept_queue = []
intercept_lock = threading.Lock()


app = Flask(__name__)

PORT = 8001

@app.route('/', methods=['GET'])
def home():
    database = sqlite3.connect('./Captured_requests.db')
    cursor = database.cursor()
    entries = cursor.execute('select * from all_requests order by Request_Number desc')
    
    return render_template("home.html", entries=entries)


@app.route("/toggle_intercept", methods=["POST"])
def toggle_intercept():
    
    global intercept_enabled
    intercept_enabled = request.json.get("enabled", False)
    return jsonify({"intercept_enabled": intercept_enabled})

@app.route("/get_intercepted_requests", methods=["GET"])
def get_intercepted_requests():
   
    global intercept_queue
    with intercept_lock:
        requests_list = [req.decode('utf-8') for req in intercept_queue]
    return jsonify({"requests": requests_list})

@app.route("/modify_request", methods=["POST"])
def modify_request():
    
    global intercept_queue

    data = request.json
    modified_request = data.get("modified_request", "").encode('utf-8')

    if intercept_queue:
        with intercept_lock:
            intercept_queue.pop(0)  

    forward_request(None, None, modified_request, None)  
    return jsonify({"status": "forwarded"})


if __name__ == "__main__":
    app.run(port=PORT)