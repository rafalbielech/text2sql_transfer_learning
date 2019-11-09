import datetime
import time
import threading
import os
import sys
import json
import argparse
from utils import *
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/evaluate", methods=['POST'])
def forward_feed():
    # capture the input from the front end
    response = request.get_json(force=True)
    # right now, only return the input uppercased
    return jsonify(result=response['data'].upper())

@app.route("/status", methods=['GET'])
def get_status():
    return jsonify(status="on")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port_number', type=int, help='the location of the original spider dataset', default=80)
    args = parser.parse_args()
    try:
        assert 80 <= args.port_number < 65000, 'port number out of bounds'
        print("Connect to http://{}:{} to access this server".format(get_ip_address(), args.port_number))

        app.run(host="0.0.0.0", port=args.port_number, debug=True)
    except Exception as e:
        print("ERROR in the start-up process:{}", e)