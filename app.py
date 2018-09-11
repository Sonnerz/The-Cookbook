import os
from config import get_uri, get_dbs_name
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = get_dbs_name()
app.config["MONGO_URI"] = get_uri()

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_test')
def get_tasks():
    return render_template("index.html", test=mongo.db.test_collection.find())

  
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)
