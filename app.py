import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "cookbook"
app.config["MONGO_URI"] = "mongodb://admin:c00k800k32-@ds251332.mlab.com:51332/cookbook"

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_test') #connection to DB. Function with decorator. Includes route to function. 
#remember the routing is a string that when attached to a URL will redirect to a particular 
#function in a flask application. 
def get_tasks():
    return render_template("test.html", test=mongo.db.test_collection.find())
  
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)
