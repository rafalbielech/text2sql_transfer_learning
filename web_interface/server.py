import sys
import os
import datetime
import json
import argparse
import torch
sys.path.append(os.path.join("..","models","sqlnet", "scripts"))
from web_utils import *
from utils import *
from flask import Flask, render_template, request, jsonify
from model.sqlnet import SQLNet
from random import sample


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

model = None
tables_json = None
data_map = None
word_emb = None
example_questions = None

def load_model(new_path):
    global model
    N_word = 50
    t1 = datetime.datetime.now()
    model = SQLNet(word_emb, N_word=N_word, gpu=False, trainable_emb = False)
    try:
        model.sel_pred.load_state_dict(torch.load(os.path.join(new_path, "sel_models.dump")))
        print("Loaded select model")
    except Exception as e:
        print("Selection model not found ", e)
    try:
        model.cond_pred.load_state_dict(torch.load(os.path.join(new_path, "cond_models.dump")))
        print("Loaded conditional model")
    except Exception as e:
        print("Conditional model not found ", e)

    try:
        model.group_pred.load_state_dict(torch.load(os.path.join(new_path, "group_models.dump")))
        print("Loaded grouping model")
    except Exception as e:
        print("Grouping model not found ", e)

    try:
        model.order_pred.load_state_dict(torch.load(os.path.join(new_path, "order_models.dump")))
        print("Loaded ordering model")
    except Exception as e:
        print("Ordering model not found ", e)
    print("Saved model initalized and loaded in {} seconds".format((datetime.datetime.now() - t1).total_seconds()))

@app.route("/")
def welcome():
    return render_template("index.html", db=sorted(load_available_dbs(data_map, 1, 90)))

@app.route("/db_change", methods=['POST'])
def reload_model():
    global model
    # get the db in question
    model = None
    response = request.get_json(force=True)
    load_model(os.path.join(args.saved_model_dir, "retrain_saved_models_{}".format(str(data_map[response['db']]))))
    return jsonify(result="done")

@app.route("/schema", methods=['POST'])
def get_schema():
    global example_questions
    # get the db in question
    response = request.get_json(force=True)
    questions = example_questions[response['db']]
    sample_questions = sample(questions, min(len(questions), 10))
    return jsonify(result=get_db_schema(tables_json, response['db']), questions=sample_questions)

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
    parser.add_argument('--tables', type=str, help='the location of the table.json file used to define schema for databases', default=os.path.join('.','tables.json'))    
    parser.add_argument('--glove_emb_dir', type=str, help="directory containing glove embeddings", default=os.path.join('..','models','sqlnet','glove'))
    parser.add_argument('--saved_model_dir', type=str, help="directory containing saved model components", default=os.path.join('.','models'))
    args = parser.parse_args()

    try:
        assert 80 <= args.port_number < 65000, 'port number out of bounds'
        print("Connect to http://{}:{} to access this server".format(get_ip_address(), args.port_number))

        tables_json = json.load(open(args.tables))
        print("Loaded tables.json file")

        example_questions = json.load(open("example_questions.json"))
        print("Loaded example_questions.json file")

        data_map = json.load(open("data.json"))
        print("Loaded data.json to table mapper")

        N_word = 50
        B_word = 6
        t1 = datetime.datetime.now()
        word_emb = load_word_emb(os.path.join(args.glove_emb_dir,  'glove.%dB.%dd.txt'%(B_word,N_word)), load_used=False, use_small=False)
        print("Word embedding loaded in {} seconds".format((datetime.datetime.now() - t1).total_seconds()))

        app.run(host="0.0.0.0", port=args.port_number, debug=False)
    except Exception as e:
        print("ERROR in the start-up process:{}", e)



