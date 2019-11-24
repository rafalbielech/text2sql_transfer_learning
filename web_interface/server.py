import sys
import os
sys.path.append(os.path.join("..","models","sqlnet", "scripts"))
import datetime
import json
import argparse
import torch
from web_utils import *
from flask import Flask, render_template, request, jsonify
from utils import *
from model.sqlnet import SQLNet

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

model = None
tables_json = None

@app.route("/")
def welcome():
    return render_template("index.html", db=get_db_names(tables_json))


@app.route("/schema", methods=['POST'])
def get_schema():
    # get the table in question
    response = request.get_json(force=True)
    return jsonify(result=get_db_schema(tables_json, response['db']))

@app.route("/evaluate", methods=['POST'])
def forward_feed():
    # capture the input from the front end
    response = request.get_json(force=True)
    # table will be found under response['table]
    # english query will be found under response['data]
    output = evaluate_one_query(model, tables_json, response['db'], response['data'])
    return jsonify(result=output)

@app.route("/status", methods=['GET'])
def get_status():
    return jsonify(status="on")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port_number', type=int, help='the location of the original spider dataset', default=80)
    parser.add_argument('--tables', type=str, help='the location of the table.json file used to define schema for databases', default=os.path.join(".","tables.json"))    
    args = parser.parse_args()
    try:
        assert 80 <= args.port_number < 65000, 'port number out of bounds'
        print("Connect to http://{}:{} to access this server".format(get_ip_address(), args.port_number))

        tables_json = json.load(open(args.tables))
        print("Loaded tables.json file")

        N_word=300
        B_word=42
        t1 = datetime.datetime.now()
        word_emb = load_word_emb(os.path.join('..','models','sqlnet','glove/glove.%dB.%dd.txt'%(B_word,N_word)), load_used=False, use_small=False)
        print("Word embedding loaded in {} seconds".format((datetime.datetime.now() - t1).total_seconds()))
        
        print("Initializing model...")
        model = SQLNet(word_emb, N_word=N_word, gpu=False, trainable_emb = False)
        
        t1 = datetime.datetime.now()
        print("Loading from sel model...")
        model.sel_pred.load_state_dict(torch.load(os.path.join("..", "models", "sqlnet", "saved_models/sel_models.dump")))
        print("Loading from cond model...")
        model.cond_pred.load_state_dict(torch.load(os.path.join("..", "models", "sqlnet", "saved_models/cond_models.dump")))
        print("Loading from group model...")
        model.group_pred.load_state_dict(torch.load(os.path.join("..", "models", "sqlnet", "saved_models/group_models.dump")))
        print("Loading from order model...")
        model.order_pred.load_state_dict(torch.load(os.path.join("..", "models", "sqlnet", "saved_models/order_models.dump")))
        print("Saved model loaded in {} seconds".format((datetime.datetime.now() - t1).total_seconds()))
        
        app.run(host="0.0.0.0", port=args.port_number, debug=False)
    except Exception as e:
        print("ERROR in the start-up process:{}", e)



