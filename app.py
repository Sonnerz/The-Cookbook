import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask_pymongo import PyMongo

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

app = Flask(__name__)
app.secret_key = 'The cat is on the roof'

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


def get_record(username):
    row={}
    try:
        row = mongo.db.user_recipe.find_one({'username': username.lower()})
    except Exception as e:
        print("error accessing DB %s"%str(e))
    
    if row:
        print("username taken")
    return row


@app.route('/')
def index():
    return render_template("index.html", test=mongo.db.test_collection.find(), users=mongo.db.user_recipe.find())


@app.route('/signup_user', methods=['POST'])
def signup_user():
    check_user = get_record(request.form.get('signupUsername'))
    if not check_user:
        users=mongo.db.user_recipe
        new_user={
                'username': request.form.get('signupUsername'),
                'password': request.form.get('signupPassword'),
                'firstname': request.form.get('firstName'),
                'lastname': request.form.get('lastName')}   
        if new_user:
            users.insert_one(new_user)
            message = "Success"
        else:
            message = "Failure"
    return redirect(url_for('index', message=message))        
    

@app.route('/login_user')
def login_user():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)

#@login_required
#@app.route('/recipe')
#def recipe():