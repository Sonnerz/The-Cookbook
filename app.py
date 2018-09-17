import os
import pdb
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.exceptions import abort, BadRequestKeyError

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
            flash("You need to be logged in, to view this page", 'info') #success error info
            return render_template("index.html")
    return wrap    

# GET RECORD FROM USERS COLLECTION
def get_record(username):
    row={}
    try:
        row = mongo.db.users.find_one({'username': username.lower()})
    except Exception as e:
        print("error accessing DB %s"%str(e))
    
    if row:
        print("one row with username does exist")
    return row

# GET RECIPES FROM RECIPE COLLECTION FOR CURRENT USER
def get_recipes(current_user_id):
    rows={}
    try:
        rows = mongo.db.recipes.find({"author" : current_user_id}) 
        #rows = mongo.db.recipes.find_one({"name" : "Chicken chasseur"})
    except Exception as e:
        print("error accessing DB %s"%str(e))
    
    if rows:
        print("recipes by author do exist")
    return rows

# GET CATEGORIES
def get_categories():
    categories=mongo.db.categories.find()
    return categories

# GET CUISINE
def get_cuisine():
    cuisine=mongo.db.cuisine.find()
    return cuisine

# GET ALLERGENS
def get_allergens():
    allergens=mongo.db.allergens.find()
    return allergens  

# INDEX
@app.route('/')
def index():
    #session.pop('username', None)
    session.pop('_flashes', None)
    return render_template("index.html", test=mongo.db.test_collection.find())

# PROFILE
@app.route('/profile')
@login_required
def profile():
    current_user = dict(get_record(session['username']))
    current_user_str = str(current_user['_id'])
    user_recipes = get_recipes(session['userid'])
    print(user_recipes)
    return render_template("profile.html", test=mongo.db.test_collection.find(), current_user=current_user, 
                            recipes=user_recipes)


# LOGOUT
@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'GET':
        print(session)
        session.pop('username', None)
        session['isLoggedin'] = False
        session.pop('_flashes', None)
        flash("You are logged out", 'success') #success error info
    return render_template("index.html", test=mongo.db.test_collection.find(), users=mongo.db.user_recipe.find())


# ADD RECIPE
@app.route('/add_recipe')
@login_required
def add_recipe():
    current_user = dict(get_record(session['username']))
    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    return render_template("addrecipe.html", test=mongo.db.test_collection.find(), current_user=current_user, 
                            categories=categories, cuisine=cuisine, allergens=allergens )    

# INSERT RECIPE IN DATABASE
@app.route('/insert_recipe', methods=['GET', 'POST'])
@login_required
def insert_recipe():
    current_user = session['userid']
    recipes = mongo.db.recipes
    new_recipe = {
        'author': current_user,       
        'name': request.form.get('name'),
        'description': request.form.get('description'),
    #     'main': request.form.get('main'),
    #     'category': request.form.get('category'),
    #     'cuisine': request.form.get('cuisine'),
    #     'diff': request.form.get('diff'),
    #     'prep': request.form.get('prep'),
    #     'cook': request.form.get('cook'),
    #     'serves': request.form.get('serves'),
    #     'calories': request.form.get('calories'),
    #     'allergen': request.form.get('allergen'),
    #     'form_user_id': request.form.get('form_user_id')
    #     })}
    recipes.insert_one(new_recipe)
    message = "updated to db" 
    return message


# SIGN UP NEW USER / REGISTER / CREATE RECORD IN COLLECTION USER_RECIPE
@app.route('/signup_user', methods=['POST'])
def signup_user():
    check_user = get_record(request.form.get('signupUsername'))
    if not check_user:
        users=mongo.db.users
        new_user={
                'username': request.form.get('signupUsername'),
                'password': request.form.get('signupPassword'),
                'firstname': request.form.get('firstName'),
                'lastname': request.form.get('lastName')} 
        #pdb.set_trace()          
        if new_user:
            users.insert_one(new_user)
            message = "success"
            return message
    else:
        message = "fail"
        return message
    return
    
# LOGIN IN USER WHO IS REGISTERED
@app.route('/login_user', methods=['POST'])
def login_user():
    pw = request.form.get('loginPassword')
    user = get_record(request.form.get('loginUsername'))
    if user and user["password"] == pw:
        # add username to flask session
        session['username'] = user['username']
        session['userid'] = str(user['_id']) #ObjectId to str
        # set session isLoggedin to True: session is true
        session['isLoggedin'] = True
        #message to user 
        message = "Welcome back " + user['username'] + " you will be redirected to your profile page."
        id = str(user['_id'])
        response = {"username": user['username'], "_id": id, "message": message}
        return jsonify(response)
    elif user and user["password"] != pw:
        message = "password wrong"
        return message
    elif not user:
        message = "no user by that name"
        return message        
    return        




if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)


    # import pdb; pdb.set_trace()
