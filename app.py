import os
# from config import get_uri, get_dbs_name
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_pymongo import PyMongo

MONGO_URI = os.getenv("MONGODB_URI")
DBS_NAME = os.getenv("DBS_NAME")


app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI
app.config["DBS_NAME"] = DBS_NAME
mongo = PyMongo(app)


@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)


@app.route('/')
@app.route('/get_test')
def get_tasks():
    return render_template("index.html", test=mongo.db.test_collection.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)
