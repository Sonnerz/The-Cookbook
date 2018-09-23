import os
import pdb
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")


app = Flask(__name__)
app.secret_key = 'The cat is on the roof'
# app.secret_key = os.urandom(24)

if app.debug:
    app.config["DBS_NAME"] = "cookbook"
    app.config["MONGO_URI"] = "mongodb://localhost:27017/cookbook"

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
def get_user(username):
    row = {}
    try:
        row = mongo.db.users.find_one({'username': username.lower()})
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if row:
        print("one row with username does exist")
    return row


# FUNCTION :: GET RECIPES FROM RECIPE COLL FOR CURRENT USER AS RECIPE AUTHOR
def get_user_recipes(current_user_id):
    rows = {}
    try:
        rows = mongo.db.recipes.find({"author": current_user_id})
        # rows = mongo.db.recipes.find_one({"name" : "Chicken chasseur"})
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("recipes by author do exist")
    return rows


# FUNCTION :: GET ALL RECIPES
def get_allrecipes():
    rows = {}
    try:
        rows = mongo.db.recipes.find()
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("all recipes found")
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
    # clear flash messages to reset
    session.pop('_flashes', None)
    return render_template("index.html", test=mongo.db.test_collection.find())


# PAGE :: PROFILE PAGE
@app.route('/profile')
@login_required
def profile():
    # get data: user, users recipes for profile page
    current_user = dict(get_user(session['username']))
    current_user_str = str(current_user['_id'])
    user_recipes = get_user_recipes(session['userid'])
    test = mongo.db.test_collection.find()
    print(test)
    return render_template("profile.html", current_user=current_user, recipes=user_recipes, test=test)


# FUNCTION :: LOGOUT FUNCTION TRIGGERED BY LOGOUT BUTTON
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # get value from get request and clear sessions values
    if request.method == 'GET':
        print(session)
        session.pop('username', None)
        session.pop('userid', None)
        session['isLoggedin'] = False
        session.pop('_flashes', None)
        # success error flash message to users
        flash("You are logged out", 'success')  
    return render_template("index.html", test=mongo.db.test_collection.find(), 
                            users=mongo.db.user_recipe.find())


# PAGE :: ADD RECIPE FORM
@app.route('/add_recipe')
@login_required
def add_recipe():
    #debug stuff
    current_user = dict(get_user(session['username']))
    ##
    # get categories, cuisine, allergens, difficulty from db for form dropdown lists
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
    # get current user id from session
    current_user_id = session['userid']
    # get all recipes to add a new recipe later
    recipes = mongo.db.recipes
    # create new recipe object
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
    # insert new recipe
    recipes.insert_one(new_recipe)
    message = "updated to db"
    return message


# PAGE :: EDIT RECIPE FORM
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    # debug stuff
    current_user = dict(get_user(session['username']))
    # get the relevant recipe form db by id passed in url
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # get categories, cuisine, allergens, difficulty from db for form dropdown lists
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
    # set userid to var, current_user_id
    current_user_id = session['userid']
    # get all recipes
    recipes = mongo.db.recipes
    # get list of ingredients from form
    ingred_list = request.form.getlist('ingredient')
    # remove blanks from list if user deletes an ingredient
    ingred_list_no_blanks = [i for i in ingred_list if i != ""]
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
    # get recipe id from the form
    recipe_id = request.form.get('recipe_id')
    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    message = "deleted"
    return message


# PAGE :: VIEW RECIPE DETAILS PAGE
@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    # get the recipe by using id passed in url
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # get categories, cuisine, allergens, difficulty for form dropdown lists
    categories = get_categories()
    cuisine = get_cuisine()
    allergens_list_of_dict = list(get_allergens())  # list of allergens dictionaries [{id:123, allergen_name:eggs}, ...]
    allergens_list = [allergen_item["allergen_name"] for allergen_item in allergens_list_of_dict]  # list comprehension used to get allergen name from allergen_list
    difficulty = get_difficulty()
    return render_template("viewrecipe.html", test=mongo.db.test_collection.find(), 
                        categories=categories, cuisine=cuisine, 
                        allergens_list=allergens_list, recipe=the_recipe, difficulty=difficulty )


# FUNCTION :: UPDATE RECIPE VOTE
@app.route('/update_vote/<recipe_id>', methods=['POST'])
def update_vote(recipe_id):
    # creates votes varialbe
    votes = None
    # get data from ajax post, set votes to data value
    votes = int(request.get_data())
    # get all recipes from db
    recipes = mongo.db.recipes
    # get the relevant recipe by its id passed in url
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # get the current votes for relevant recipe. Change to integer for addition in next step
    current_vote = int(this_recipe['votes'])
    # create new_vote var and add new vote to current recipe vote
    new_vote = current_vote + votes
    # update the relevant recipe with the new vote
    recipes.update_one({'_id': ObjectId(recipe_id)},
    {'$set':
        {
            'votes': new_vote
        }
    })
    # get the recipe again with updated votes
    this_recipe_updated = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # get the new votes value
    updated_recipe_vote = this_recipe_updated['votes']
    # pass the update vote value back to the ajax for to update the html page
    return str(updated_recipe_vote)


# PAGE :: RECIPE SEARCH PAGE
@app.route('/recipesearch', methods=['POST', 'GET'])
def recipesearch():
    recipes = get_allrecipes()
    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    difficulty = get_difficulty()
    return render_template("recipesearch.html", test=mongo.db.test_collection.find(), 
                            recipes=recipes, categories=categories,
                            cuisine=cuisine, allergens=allergens)



# FUNCTION :: GET RECIPES BY CATEGORY
@app.route('/filter_by_category/<category>', methods=['POST', 'GET'])
def filter_by_category(category):
    filteredRecipes = None
    category_name = category
    print("category_name 33333>>> ", category_name)
    try:
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({"category": category_name})]
    except Exception as e:
        print("error accessing DB to find category %s" % str(e))

    if filteredRecipes:
        print("recipes by category exist")
        for recipe in filteredRecipes:
            print(recipe['name'])
    else:
        print("no recipes found")

    # result_to_return = []
    for recipe in filteredRecipes:
        recipe['_id']= str(recipe['_id'])
        result_to_return = recipe
        print(type(result_to_return))

    return jsonify(result_to_return)




# FUNCTION :: SIGN UP NEW USER / REGISTER / CREATE RECORD IN USERS COLLECTION
@app.route('/signup_user', methods=['POST'])
def signup_user():
    # query db to see if username already exists
    check_user = get_user(request.form.get('signupUsername'))
    # if that username is not in db then create new user object and add new user
    if not check_user:
        users = mongo.db.users
        new_user = {
                'username': request.form.get('signupUsername'),
                'password': request.form.get('signupPassword'),
                'firstname': request.form.get('firstName'),
                'lastname': request.form.get('lastName')} 
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
    # get data from ajax post
    pw = request.form.get('loginPassword')
    user = get_user(request.form.get('loginUsername'))
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