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
# app.secret_key = os.urandom(24)

if app.debug:
    app.config["DBS_NAME"] = "cookbook"
    app.config["MONGO_URI"] = "mongodb://c00l3:BGirl808@ds251332.mlab.com:51332/cookbook"
    # app.config["DBS_NAME"] = DBS_NAME
    # app.config["MONGO_URI"] = MONGO_URI
else:
    app.config["DBS_NAME"] = DBS_NAME
    app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


# DEBUGGING
@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)


# PAGE :: ADD RECIPE FORM
@app.route('/content_to_tab')
def content_to_tab():
    return render_template("content_to_tab.html")

# FUNCTION :: LOGIN REQUIRED WRAP
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('isLoggedin'):
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in, to view this page", 'info')
            return render_template("index.html")
    return wrap


# FUNCTION :: GET RECORD FROM USERS COLLECTION BY USERNAME
def get_record(username):
    row = {}
    try:
        row = mongo.db.users.find_one({'username': username.lower()})
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if row:
        print("one row with username does exist")
    return row


# FUNCTION :: GET RECIPES FROM RECIPE COLL FOR CURRENT USER AS RECIPE AUTHOR
def get_recipes(current_user_id):
    rows = {}
    try:
        rows = mongo.db.recipes.find({"author": current_user_id})
        # rows = mongo.db.recipes.find_one({"name" : "Chicken chasseur"})
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("recipes by author do exist")
    return rows


# FUNCTION :: GET CATEGORIES
def get_categories():
    categories = mongo.db.categories.find()
    return categories


# FUNCTION :: GET CUISINE
def get_cuisine():
    cuisine = mongo.db.cuisine.find()
    return cuisine


# FUNCTION :: GET ALLERGENS
def get_allergens():
    allergens = mongo.db.allergens.find()
    return allergens


# FUNCTION :: GET DIFFICULTY OPTIONS
def get_difficulty():
    difficulty = mongo.db.difficulty.find()
    return difficulty


# PAGE :: INDEX - HOME PAGE
@app.route('/')
def index():
    # session.pop('username', None)
    session.pop('_flashes', None)
    return render_template("index.html", test=mongo.db.test_collection.find())


# PAGE :: PROFILE PAGE
@app.route('/profile')
@login_required
def profile():
    current_user = dict(get_record(session['username']))
    current_user_str = str(current_user['_id'])
    user_recipes = get_recipes(session['userid'])
    return render_template("profile.html", test=mongo.db.test_collection.find(),
                            current_user=current_user, recipes=user_recipes)


# FUNCTION :: LOGOUT FUNCTION TRIGGERED BY LOGOUT BUTTON
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'GET':
        print(session)
        session.pop('username', None)
        session['isLoggedin'] = False
        session.pop('_flashes', None)
        flash("You are logged out", 'success')  # success error info
    return render_template("index.html", test=mongo.db.test_collection.find(), 
                            users=mongo.db.user_recipe.find())


# PAGE :: ADD RECIPE FORM
@app.route('/add_recipe')
@login_required
def add_recipe():
    #debug stuff
    current_user = dict(get_record(session['username']))
    ##

    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    difficulty = get_difficulty()
    return render_template("addrecipe.html", test=mongo.db.test_collection.find(),
                            current_user=current_user,
                            categories=categories, cuisine=cuisine,
                            allergens=allergens, difficulty=difficulty)


# FUNCTION :: INSERT RECIPE IN RECIPES COLLECTION IN DATABASE
@app.route('/insert_recipe', methods=['GET', 'POST'])
@login_required
def insert_recipe():
    current_user_id = session['userid']
    recipes = mongo.db.recipes
    new_recipe = {
        'author': current_user_id,       
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'main_ingredient': request.form.get('main_ingredient'),
        'category': request.form.get('category'),
        'cuisine': request.form.get('cuisine'),
        'difficulty': request.form.get('difficulty'),
        'prep_time': request.form.get('prep_time'),
        'cook_time': request.form.get('cook_time'),
        'serves': request.form.get('serves'),
        'calories': request.form.get('calories'),
        'allergens': request.form.getlist('allergen'),
        'ingredients': request.form.getlist('ingredient'),
        'instructions': request.form.getlist('instruction'),
        'image_url': request.form.get('image_url'),
        'views': 0,
        'votes': 0
    }
    recipes.insert_one(new_recipe)
    message = "updated to db"
    return message


# PAGE :: EDIT RECIPE FORM
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    print(recipe_id)
    # debug stuff
    current_user = dict(get_record(session['username']))
    ##
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = get_categories()
    cuisine = get_cuisine()
    allergens_list_of_dict = list(get_allergens())  # list of allergens dictionaries [{id:123, allergen_name:eggs}, ...]
    allergens_list = [allergen_item["allergen_name"] for allergen_item in allergens_list_of_dict] #  list comprehension used to get allergen name from allergen_list
    difficulty = get_difficulty()
    return render_template("editrecipe.html",
                            test=mongo.db.test_collection.find(),
                            current_user=current_user,
                            categories=categories,
                            cuisine=cuisine,
                            allergens_list=allergens_list,
                            recipe=the_recipe,
                            difficulty=difficulty)


# FUNCTION :: UPDATE RECIPE WRITE BACK TO RECIPES COLLECION IN DATABASE
@app.route('/update_recipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    current_user_id = session['userid']
    recipes = mongo.db.recipes
    ingred_list = request.form.getlist('ingredient')
    ingred_list_no_blanks = [i for i in ingred_list if i != ""] # remove blanks from list if user deletes one
    recipes.update_one({'_id': ObjectId(recipe_id)},
    {'$set':
        {
            'author': current_user_id,
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'main_ingredient': request.form.get('main_ingredient'),
            'category': request.form.get('category'),
            'cuisine': request.form.get('cuisine'),
            'difficulty': request.form.get('difficulty'),
            'prep_time': request.form.get('prep_time'),
            'cook_time': request.form.get('cook_time'),
            'serves': request.form.get('serves'),
            'calories': request.form.get('calories'),
            'allergens': request.form.getlist('allergen'),
            'ingredients': ingred_list_no_blanks,
            'instructions': request.form.getlist('instruction'),
            'image_url': request.form.get('image_url'),
            'views': request.form.get('views'),
            'votes': request.form.get('votes')
        }
    })
    flash("recipe upated")
    message = "success update"
    return message


# FUNCTION :: DELETE RECIPE TRIGGERED BY DELETE BUTTON ON PROFILE PAGE
@app.route('/delete_recipe', methods=['POST'])
def delete_recipe():
    recipe_id = request.form.get('recipe_id')
    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    message = "deleted"
    return message


# PAGE :: VIEW RECIPE DETAILS PAGE
@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    print(recipe_id)
    # debug stuff
    #current_user = dict(get_record(session['username']))
    ##
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = get_categories()
    cuisine = get_cuisine()
    allergens_list_of_dict = list(get_allergens())  # list of allergens dictionaries [{id:123, allergen_name:eggs}, ...]
    allergens_list = [allergen_item["allergen_name"] for allergen_item in allergens_list_of_dict]  # list comprehension used to get allergen name from allergen_list
    difficulty = get_difficulty()
    return render_template("viewrecipe.html", test=mongo.db.test_collection.find(), 
                        categories=categories, cuisine=cuisine, 
                        allergens_list=allergens_list, recipe=the_recipe, difficulty=difficulty )


# FUNCTION :: SIGN UP NEW USER / REGISTER / CREATE RECORD IN USERS COLLECTION
@app.route('/signup_user', methods=['POST'])
def signup_user():
    check_user = get_record(request.form.get('signupUsername'))
    if not check_user:
        users = mongo.db.users
        new_user = {
                'username': request.form.get('signupUsername'),
                'password': request.form.get('signupPassword'),
                'firstname': request.form.get('firstName'),
                'lastname': request.form.get('lastName')} 
        # pdb.set_trace()
        if new_user:
            users.insert_one(new_user)
            message = "success"
            return message
    else:
        message = "fail"
        return message
    return


# FUNCTION :: LOGIN IN USER WHO IS REGISTERED TRIGGERED BY LOGIN BUTTON
@app.route('/login_user', methods=['POST'])
def login_user():
    pw = request.form.get('loginPassword')
    user = get_record(request.form.get('loginUsername'))
    if user and user["password"] == pw:
        # add username to flask session
        session['username'] = user['username']
        session['userid'] = str(user['_id'])  # ObjectId to str
        # set session isLoggedin to True: session is true
        session['isLoggedin'] = True
        # message to user
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
    app.run(host=os.environ.get('IP'), 
            port=int(os.environ.get('PORT')), 
            debug=True)


# import pdb; pdb.set_trace()