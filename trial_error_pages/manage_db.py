import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "cookbook"
app.config["MONGO_URI"] = "mongodb://admin:c00k800k32-@ds251332.mlab.com:51332/cookbook"

mongo = PyMongo(app)


def insert_category():
    categories = mongo.db.categories
    category_doc = {'category_name' : "Brunch"}
    categories.insert_one(category_doc)
  
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)