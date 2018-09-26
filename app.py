import os
import pdb
import pymongo
import math
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util
from datetime import datetime
from math import ceil


DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")


app = Flask(__name__)
app.secret_key = 'The cat is on the roof'
# app.secret_key = os.urandom(24)

if app.debug:
    app.config["DBS_NAME"] = "cookbook"
    # app.config["MONGO_URI"] = "mongodb://localhost:27017/cookbook"
    app.config["MONGO_URI"] = "mongodb://c00l33:eZc727sZ7XmixRH@ds251332.mlab.com:51332/cookbook"
    
else:
    app.config["DBS_NAME"] = DBS_NAME
    app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


# DEBUGGING
@app.context_processor
def debug_on_off():
    return dict(debug=app.debug)

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
        # rows = mongo.db.recipes.find({"author": current_user_id})
        rows = [recipe for recipe in mongo.db.recipes.find({'$query': {'author': current_user_id}, '$orderby': { 'votes' : -1 } })]
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


# FUNCTION :: GET RECIPES WITH HIGHEST VOTES x4
def get_votes_recipes():
    rows = {}
    try:
        rows = mongo.db.recipes.find().sort('votes', -1).limit(4)
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("all recipes found")
    return rows


# FUNCTION :: GET 8 RANDOM RECIPES
def get_random_recipes():
    rows = {}
    try:
        # Query recipes collection and return ordered by votes descending
        rows = mongo.db.recipes.aggregate([{'$sample': {'size': 8}},{'$sort':{'votes': -1}}])
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("all recipes found")
    return rows


# FUNCTION :: GET RECENT RECIPES x4
def get_recent_recipes():
    rows = {}
    try:
        # Query recipes collection and return ordered by votes descending
       rows = mongo.db.recipes.find().sort('_id',-1).limit(4)
    except Exception as e:
        print("error accessing DB %s" % str(e))

    if rows:
        print("latest 3 recipes found")
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
        'image_url': request.form.get('image_url'),
        'description': request.form.get('description'),
        'main_ingredient': request.form.get('main_ingredient').lower(),
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
        'votes': 0
    }
    # insert new recipe
    recipes.insert_one(new_recipe)
    message = "updated to db"
    return message


# PAGE :: EDIT RECIPE FORM
@app.route('/edit_recipe/<recipe_id>')
@login_required
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
@login_required
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
            'image_url': request.form.get('image_url'),
            'description': request.form.get('description'),
            'main_ingredient': request.form.get('main_ingredient').lower(),
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
            'votes': request.form.get('votes')
        }
    })
    flash("recipe upated")
    message = "success update"
    return message


# FUNCTION :: DELETE RECIPE TRIGGERED BY DELETE BUTTON ON PROFILE PAGE
@app.route('/delete_recipe', methods=['POST'])
@login_required
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
    the_author = mongo.db.users.find_one({"_id":  ObjectId(the_recipe['author'])})
    print(the_author)
    # get categories, cuisine, allergens, difficulty for form dropdown lists
    categories = get_categories()
    cuisine = get_cuisine()
    allergens_list_of_dict = list(get_allergens())  # list of allergens dictionaries [{id:123, allergen_name:eggs}, ...]
    allergens_list = [allergen_item["allergen_name"] for allergen_item in allergens_list_of_dict]  # list comprehension used to get allergen name from allergen_list
    difficulty = get_difficulty()
    return render_template("viewrecipe.html", test=mongo.db.test_collection.find(), 
                        categories=categories, cuisine=cuisine, 
                        allergens_list=allergens_list, recipe=the_recipe, 
                        difficulty=difficulty, recipeauthor=the_author)


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


# PAGE :: MY RECIPES
@app.route('/myrecipes')
def myrecipes():
    # get data: user, users recipes for myrecipes page
    current_user = dict(get_user(session['username']))
    test = mongo.db.test_collection.find()

     # initiate the data, search recipes by author
    user_recipes_starting_id = [recipe for recipe in mongo.db.recipes.find({'author': session['userid']})]
    for r in user_recipes_starting_id:
        print(r['name'])

    if not user_recipes_starting_id:
        return render_template("myrecipes.html", current_user=current_user, test=test)

    
    # START PAGING - set offset and limit from url
    offset = int(request.args['offset'])
    limit  = int(request.args['limit'])

    # get total count of recipes for this author
    total_count=len(user_recipes_starting_id)
    # get last id displayed using _id as identifier
    last_id = user_recipes_starting_id[offset]['_id']
    # get updated data greater than the last doc _id displayed
    recipes = [recipe for recipe in mongo.db.recipes.find({'$and': [{'author': session['userid']}, {'_id': {'$gte': last_id}}]}).limit(limit)]

    next_url=""
    prev_url=""

    number_of_pages = int(math.ceil(total_count/limit))
    # conditionally display the next & previous links
    if limit < total_count:
        if offset + limit < total_count:
            next_url = '/myrecipes?limit=' + str(limit) + '&offset=' + str(offset + limit)

        if offset + limit > total_count-limit:
            prev_url = '/myrecipes?limit=' + str(limit) + '&offset=' + str(offset - limit)
    return render_template("myrecipes.html", current_user=current_user, test=test, number_of_pages=number_of_pages, total_count=total_count, recipes=recipes, prev_url=prev_url, next_url=next_url)


# PAGE :: RECIPE SEARCH PAGE
@app.route('/recipesearch', methods=['POST', 'GET'])
def recipesearch():
    # Show 3 most recent recipes
    recent_recipes = get_recent_recipes()
    # Show 3 recipes with highest votes
    highest_voted_recipe = get_votes_recipes()
    # Show 12 random recipes on recipe search that change when page refreshes
    recipes = get_random_recipes()
    # get categories, cuisines, allergens, difficulty for dropdown filtering options
    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    difficulty = get_difficulty()
    return render_template("recipesearch.html", test=mongo.db.test_collection.find(), 
                            recipes=recipes, categories=categories,
                            cuisine=cuisine, allergens=allergens,
                            recentrecipes=recent_recipes, highestvotes=highest_voted_recipe)


# FUNCTION :: GET RECIPES BY CATEGORY
@app.route('/filter_by_category/<category>', methods=['POST', 'GET'])
def filter_by_category(category):
    filteredRecipes = None
    category_name = category
    print("category_name 6>>> ", category_name)
    try:
        # filteredRecipes = [recipe for recipe in mongo.db.recipes.find({"category": category_name})]
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({'$query': {'category': category_name}, '$orderby': { 'votes' : -1 } })]

    except Exception as e:
        print("error accessing DB to find category %s" % str(e))

    if filteredRecipes:
        print("recipes by category exist")
        # for r in filteredRecipes:
        #     r['_id']= str(r['_id'])
        #     result = r
        #     print(result['name'])
        # filteredRecipes.append(r)
        return render_template("resultTemplate.html", reciperesults=filteredRecipes)    
    else:
        print("no recipes with that category found")
        message = "no recipes with that " + category_name + " found"
        return message


# FUNCTION :: GET RECIPES BY CUISINE
@app.route('/filter_by_cuisine/<cuisine>', methods=['POST', 'GET'])
def filter_by_cuisine(cuisine):
    filteredRecipes = None
    cuisine_name = cuisine
    print("cuisine 6>>> ", cuisine_name)
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({'$query': {'cuisine': cuisine_name}, '$orderby': { 'votes' : -1 } })]
    except Exception as e:
        print("error accessing DB to find cuisine %s" % str(e))

    if filteredRecipes:
        print("recipes by cuisine exist")
        return render_template("resultTemplate.html", reciperesults=filteredRecipes)    
    else:
        print("no recipes with that cuisine found")
        message = "no recipes with that" + cuisine_name + "found"
        return message
 

# FUNCTION :: GET RECIPES BY ALLERGEN
@app.route('/filter_by_allergen/<allergen>', methods=['POST', 'GET'])
def filter_by_allergen(allergen):
    filteredRecipes = None
    allergen_name = allergen
    print("allergen 6>>> ", allergen_name)
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({'$query': {'allergens': allergen_name}, '$orderby': { 'votes' : -1 } })]
    except Exception as e:
        print("error accessing DB to find allergen %s" % str(e))

    if filteredRecipes:
        print("recipes by allergen exist")
        return render_template("resultTemplate.html", reciperesults=filteredRecipes)    
    else:
        print("no recipes with that allergen found")
        message = "no recipes with that" + allergen_name + "found"
        return message


# FUNCTION :: GET RECIPES BY INGREDIENT
@app.route('/filter_by_ingredient', methods=['POST', 'GET'])
def filter_by_ingredient():
    filteredRecipes = None
    # convert to string and lower()
    ingredient_name = str(request.get_data()).lower()
    # remove b from search text
    ingredient_name = ingredient_name[1:]
    # remove quotes ' ' from either end of search text
    ingredient_name = ingredient_name.strip('\'')
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({'$query': {'main_ingredient': ingredient_name}, '$orderby': { 'votes' : -1 } })]
    except Exception as e:
        print("error accessing DB to find ingredient name %s" % str(e))

    if filteredRecipes:
        print("recipes by ingredient exist")
        return render_template("resultTemplate.html", reciperesults=filteredRecipes)    
    else:
        print("no recipes with that ingredient found")
        message = "no recipes with that" + ingredient_name + "found"
        return message


# FUNCTION :: GET RECIPES BY CATEGORY & CUISINE
@app.route('/filter_by_catcuis/<value1><value2>', methods=['POST', 'GET'])
def filter_by_catcuis(value):
    filteredRecipes = None
    category = value1
    cuisine = value2
    print(category, cuisine)
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find({'$query': {{'category': category}, {'cuisine': cuisine}},'$orderby': { 'votes' : -1 } })]
    except Exception as e:
        print("error accessing DB to find allergen %s" % str(e))

    if filteredRecipes:
        print("recipes by allergen exist")
        return render_template("resultTemplate.html", reciperesults=filteredRecipes)    
    else:
        print("no recipes with that allergen found")
        message = "no recipes with that" + allergen_name + "found"
        return message



# FUNCTION :: SIGN UP NEW USER / REGISTER / CREATE RECORD IN USERS COLLECTION
@app.route('/signup_user', methods=['POST'])
def signup_user():
    # query db to see if username already exists
    check_user = get_user(request.form.get('signupUsername'))
    # if that username is not in db then create new user object and add new user
    if not check_user:
        users = mongo.db.users
        new_user = {
                'username': request.form.get('signupUsername').lower(),
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
    user = get_user(request.form.get('loginUsername').lower())
    if user and user["password"] == pw:
        # add username to flask session
        session['username'] = user['username']
        session['userid'] = str(user['_id'])  # ObjectId to str
        # set session isLoggedin to True: session is true
        session['isLoggedin'] = True
        # message to user
        message = "Welcome back " + user['username'] + " you will be redirected to your myrecipes page."
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


@app.errorhandler(404)
def page_not_found(error):
    '''
    404 error is redirected to 404.html
    '''
    return render_template('404.html')


@app.errorhandler(500)
def internal_error(error):
    '''
    500 error is redirected to 500.html
    '''
    session.pop('_flashes', None)
    session.pop('username', None)
    return render_template('500.html') 
    


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), 
            port=int(os.environ.get('PORT')), 
            debug=True)


# import pdb; pdb.set_trace()

# PAGE :: MY RECIPES
# @app.route('/myrecipes')
# @login_required
# def myrecipes():
#     # get data: user, users recipes for myrecipes page
#     current_user = dict(get_user(session['username']))
#     current_user_str = str(current_user['_id'])
#     user_recipes = get_user_recipes(session['userid'])
#     test = mongo.db.test_collection.find()
#     print(test)
#     return render_template("myrecipes.html", current_user=current_user, recipes=user_recipes, test=test)