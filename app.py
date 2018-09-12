import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_pymongo import PyMongo

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

app = Flask(__name__)

if app.debug:
    app.config["DBS_NAME"] = "cookbook"
    app.config["MONGO_URI"] = "mongodb://admin:c00k800k32-@ds251332.mlab.com:51332/cookbook"
else:
    app.config["DBS_NAME"] = DBS_NAME
    app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)


@app.route('/')
@app.route('/get_test')
def get_tasks():
    return render_template("index.html", test=mongo.db.test_collection.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=False)
