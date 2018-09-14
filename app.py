import os
import pdb
from functools import wraps
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

# DEBUGGING
@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)

# LOGIN REQUIRED WRAP
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('isLoggedin') == True:    
            return f(*args, **kwargs)
        else:
            flash("you need to be logged in first")
            return redirect(url_for('index'))
    return wrap    

# GET RECORD FROM USER_RECIPE COLLECTION
def get_record(username):
    row={}
    try:
        row = mongo.db.user_recipe.find_one({'username': username.lower()})
    except Exception as e:
        print("error accessing DB %s"%str(e))
    
    if row:
        print("row exists")
    return row

# INDEX
@app.route('/')
def index():
    #session.pop('username', None)
    session.pop('_flashes', None)
    return render_template("index.html", test=mongo.db.test_collection.find(), users=mongo.db.user_recipe.find())

# PROFILE
@app.route('/profile')
@login_required
def profile():
    current_user = get_record(session['username'])
    return render_template("profile.html", test=mongo.db.test_collection.find(), current_user=current_user)

# LOGOUT
@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'GET':
        print(session)
        session.pop('username', None)
        session['isLoggedin'] = False
        session.pop('_flashes', None)
    return render_template("index.html", test=mongo.db.test_collection.find(), users=mongo.db.user_recipe.find())


# SIGN UP NEW USER / REGISTER / CREATE RECORD IN COLLECTION USER_RECIPE
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
        #pdb.set_trace()          
        if new_user:
            users.insert_one(new_user)
            message = "Success"
            return message
    else:
        message = "Failure name take"
        return message
    return
    
# LOGIN IN USER WHO IS REGISTERED
@app.route('/login_user', methods=['POST'])
def login_user():
    pw = request.form.get('loginPassword')
    user = get_record(request.form.get('loginUsername'))
    if user and user["password"] == pw:
        # message = "Welcome back " + user['username']
        # add username to flask session
        session['username'] = user['username']
        session['isLoggedin'] = True
        message = "Welcome back " + user['username']
        return message        
    elif user and user["password"] != pw:
        message = "password wrong"
        return message
    elif not user:
        message = "no user by that name"
        return message        
    return        



if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)