import os
import pdb
import pymongo
import math
import werkzeug.security
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import Flask, render_template, request, flash, redirect,\
    url_for, session, jsonify, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util
from datetime import datetime
from math import ceil
from stats.statistics import cuis_dataframe, cat_dataframe

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

app = Flask(__name__)
app.debug = False

if app.debug:
    from config import config
    app.secret_key = config()
    app.config["DBS_NAME"] = "cookbook"
    app.config["MONGO_URI"] = "mongodb://localhost:27017/cookbook"
else:
    app.secret_key = os.getenv('SECRET_KEY')
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


# FUNCTION :: COMPARE PASSWORD
def compare_password(hashedpw, formpw):
    compare_pw = check_password_hash(hashedpw, formpw)
    return compare_pw


# FUNCTION :: GET USER FROM USERS COLLECTION BY USERNAME
def get_user(username):
    row = {}
    try:
        row = mongo.db.users.find_one({'username': username.lower()})
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if row:
        print("one row with username does exist")
    return row


# FUNCTION :: GET RECIPES FROM RECIPE COLL FOR CURRENT USER AS RECIPE AUTHOR
def get_user_recipes(current_user_id):
    rows = {}
    try:
        # rows = mongo.db.recipes.find({"author": current_user_id})
        rows = [recipe for recipe in mongo.db.recipes.find(
            {
                '$query':
                {
                    'author': current_user_id}, '$orderby': {'votes': -1}
                }
            )]
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if rows:
        print("recipes by author do exist")
    return rows


# FUNCTION :: GET ALL RECIPES
def get_allrecipes():
    rows = {}
    try:
        rows = mongo.db.recipes.find()
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if rows:
        print("all recipes found")
    return rows


# FUNCTION :: GET RECIPES WITH HIGHEST VOTES
def get_votes_recipes():
    rows = {}
    try:
        rows = mongo.db.recipes.find().sort('votes', -1).limit(3)
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if rows:
        print("all recipes found by highest votes")
    return rows


# FUNCTION :: GET RANDOM RECIPES
def get_random_recipes():
    random_recipes = {}
    try:
        # Query recipes collection and return ordered by votes descending
        random_recipes = [
            random_recipe for random_recipe in mongo.db.recipes.aggregate(
                [
                    {'$sample': {'size': 8}}, {'$sort': {'votes': -1}}
                ]
            )]
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if random_recipes:
        print("all random recipes found")
    return random_recipes


# FUNCTION :: GET MOST RECENT RECIPES
def get_recent_recipes():
    recipes = {}
    try:
        # Query recipes collection and return ordered by votes descending
        recipes = [
            recipe for recipe in mongo.db.recipes.find()
            .sort('_id', -1).limit(3)]
    except Exception as e:
        # print("error accessing DB %s" % str(e))
        return render_template("500.html")

    if recipes:
        print("latest 3 recipes found")
    return recipes


# FUNCTION :: GET RECIPE AUTHOR USERNAME
def get_recipe_author_username(cursor):
    author_id = []
    # for recipe in mongo.db.recipes.find():
    #     author_id.append((recipe['_id'], recipe['author']))
    for recipe in cursor:
        author_id.append((recipe['_id'], recipe['author']))

    for id, item in author_id:
        recipe = mongo.db.recipes.find_one({"_id": id})
        authorname = mongo.db.users.find_one(
            {"_id": ObjectId(item)}, {"username": 1})
        username = {recipe: authorname}
        for u in username:
            print(u)
    return username


# FUNCTION :: GET CATEGORIES
def get_categories():
    try:
        categories = [category for category in mongo.db.categories.find()]
    except:
        return render_template("500.html")
    return categories


# FUNCTION :: GET CUISINE
def get_cuisine():
    try:
        cuisine = [cuisine for cuisine in mongo.db.cuisine.find()]
    except:
        return render_template("500.html")
    return cuisine


# FUNCTION :: GET ALLERGENS
def get_allergens():
    try:
        allergens = [allergen for allergen in mongo.db.allergens.find()]
    except:
        return render_template("500.html")
    return allergens


# FUNCTION :: GET DIFFICULTY OPTIONS
def get_difficulty():
    try:
        difficulty = [difficulty for difficulty in mongo.db.difficulty.find()]
    except:
        return render_template("500.html")
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
    # debug stuff
    current_user = dict(get_user(session['username']))
    # get categories, cuisine, allergens, difficulty from db for form dropdown
    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    difficulty = get_difficulty()
    return render_template("addrecipe.html",
                           test=mongo.db.test_collection.find(),
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
    # get list of ingredients from form
    ingred_list = request.form.getlist('ingredient')
    # remove blanks from list if user add a blank input
    ingred_list_no_blanks = [i for i in ingred_list if i != ""]
    # get list of instructions from form
    instruct_list = request.form.getlist('instruction')
    # remove blanks from list if user deletes an ingredient
    instruct_list_no_blanks = [i for i in instruct_list if i != ""]
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
        'ingredients': ingred_list_no_blanks,
        'instructions': instruct_list_no_blanks,
        'votes': int(0),
        'dateCreated': datetime.now(),
        'dateModified': datetime.now()
    }
    # insert new recipe
    recipes.insert_one(new_recipe)
    message = "Your recipe has been added."
    return message


# PAGE :: EDIT RECIPE FORM
@app.route('/edit_recipe/<recipe_id>')
@login_required
def edit_recipe(recipe_id):
    # debug stuff
    current_user = dict(get_user(session['username']))
    # get the relevant recipe form db by id passed in url
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # get categories, cuisine, allergens, difficulty from db for form dropdown
    categories = get_categories()
    cuisine = get_cuisine()
    # list of allergens dictionaries [{id:123, allergen_name:eggs}, ...]
    allergens_list_of_dict = list(get_allergens())
    # list comprehension used to get allergen name from allergen_list
    allergens_list = [allergen_item["allergen_name"]
                      for allergen_item in allergens_list_of_dict]
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
    try:
        # get all recipes
        recipes = mongo.db.recipes
    except:
        return render_template("500.html")
    # get list of ingredients from form
    ingred_list = request.form.getlist('ingredient')
    # remove blanks from list if user deletes an ingredient
    ingred_list_no_blanks = [i for i in ingred_list if i != ""]
    # get list of instructions from form
    instruct_list = request.form.getlist('instruction')
    # remove blanks from list if user deletes an ingredient
    instruct_list_no_blanks = [i for i in instruct_list if i != ""]
    recipes.update_one({'_id': ObjectId(recipe_id)},
                       {'$set':
                        {
                                'author': current_user_id,
                                'name': request.form.get('name'),
                                'image_url': request.form.get('image_url'),
                                'description': request.form.get('description'),
                                'main_ingredient': request.form.get(
                                    'main_ingredient').lower(),
                                'category': request.form.get('category'),
                                'cuisine': request.form.get('cuisine'),
                                'difficulty': request.form.get('difficulty'),
                                'prep_time': request.form.get('prep_time'),
                                'cook_time': request.form.get('cook_time'),
                                'serves': request.form.get('serves'),
                                'calories': request.form.get('calories'),
                                'allergens': request.form.getlist('allergen'),
                                'ingredients': ingred_list_no_blanks,
                                'instructions': instruct_list_no_blanks,
                                'votes': int(request.form.get('votes')),
                                'dateModified': datetime.now()
                         }
                        }
                       )
    message = "The recipe has been updated."
    return message


# FUNCTION :: DELETE RECIPE TRIGGERED BY DELETE BUTTON ON PROFILE PAGE
@app.route('/delete_recipe', methods=['POST'])
@login_required
def delete_recipe():
    # get recipe id from the form
    recipe_id = request.form.get('recipe_id')
    try:
        mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    except:
        return render_template("500.html")
    message = "deleted"
    return message


# PAGE :: VIEW RECIPE DETAILS PAGE
@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    # get the recipe by using id passed in url
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    the_author = mongo.db.users.find_one(
        {"_id": ObjectId(the_recipe['author'])
         })
    # get categories, cuisine, allergens, difficulty for form dropdown lists
    categories = get_categories()
    cuisine = get_cuisine()
    # list of allergens dictionaries [{id:123, allergen_name:eggs},...]
    allergens_list = list(get_allergens())
    # list comprehension used to get allergen name from allergen_list
    allergens_list = [allergen_item["allergen_name"]
                      for allergen_item in allergens_list]
    difficulty = get_difficulty()
    return render_template("viewrecipe.html",
                           test=mongo.db.test_collection.find(),
                           categories=categories, cuisine=cuisine,
                           allergens_list=allergens_list, recipe=the_recipe,
                           difficulty=difficulty, recipeauthor=the_author)


# FUNCTION :: UPDATE RECIPE VOTE
@app.route('/update_vote/<recipe_id>', methods=['POST'])
def update_vote(recipe_id):
    # check that user has not voted for recipe previously
    current_user = session['username']
    recipes_voted_for = get_user(current_user)
    # if recipe id is in recipe_votes, person cannot vote
    if recipe_id in recipes_voted_for['recipe_votes']:
        message = 'fail'
        return message
    else:
        # creates votes variable
        votes = None
        # get data from ajax post, set votes to data value
        votes = int(request.get_data())
        # get the relevant recipe by its id passed in url
        this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        # get the current votes for this recipe.
        # Change to integer for addition in next step
        current_vote = int(this_recipe['votes'])
        # create new_vote var and add new vote to current recipe vote
        new_vote = current_vote + votes
        # update the relevant recipe with the new vote
        mongo.db.recipes.update_one({'_id': ObjectId(recipe_id)},
                                    {'$set':
                                        {
                                            'votes': new_vote
                                        }
                                     })
        # update the users list of voted recipes
        mongo.db.users.update_one({"username": current_user},
                                  {'$push':
                                   {
                                        'recipe_votes': recipe_id
                                    }
                                   })
        # get the recipe again with updated votes
        this_recipe_updated = mongo.db.recipes.find_one(
                                {"_id": ObjectId(recipe_id)})
        # get the new votes value
        updated_recipe_vote = this_recipe_updated['votes']
        # pass the update vote value back to ajax to update the html page
        return str(updated_recipe_vote)


# PAGE :: MY RECIPES
@app.route('/myrecipes')
@login_required
def myrecipes():
    # Pagination code found: https://www.youtube.com/watch?v=Lnt6JqtzM7I

    # get data: user, users recipes for myrecipes page
    current_user = dict(get_user(session['username']))
    test = mongo.db.test_collection.find()

    # initiate the data, search recipes by author
    user_recipes_starting_id = [recipe for recipe in mongo.db.recipes.find(
                                {'author': session['userid']})]
    # get total count of recipes for this author
    total_count = len(user_recipes_starting_id)

    if not user_recipes_starting_id:
        return render_template("myrecipes.html", total_count=total_count)

    # START PAGING - set offset and limit from url
    offset = int(request.args['offset'])
    limit = int(request.args['limit'])

    # get last id displayed using _id as identifier
    try:
        last_id = user_recipes_starting_id[offset]['_id']
    except:
        flash = ('You have' + str(total_count) + 'recipes')
        newurl = 'myrecipes?limit=5&offset=0'
        return redirect(newurl)

    # get updated data greater than the last doc _id displayed
    recipes = [recipe for recipe in mongo.db.recipes.find(
        {'$and': [{'author': session['userid']},
                  {'_id': {'$gte': last_id}}]}).limit(limit)]

    next_url = ""
    prev_url = ""

    number_of_pages = int(math.ceil(total_count/limit))

    next_url = '/myrecipes?limit=' + str(limit) + \
        '&offset=' + str(offset + limit)
    prev_url = '/myrecipes?limit=' + str(limit) + \
        '&offset=' + str(offset - limit)

    return render_template("myrecipes.html",
                           current_user=current_user,
                           test=test,
                           number_of_pages=number_of_pages,
                           total_count=total_count,
                           recipes=recipes,
                           prev_url=prev_url, next_url=next_url)


# PAGE :: RECIPE SEARCH PAGE
@app.route('/recipesearch', methods=['POST', 'GET'])
def recipesearch():
    # Show 3 most recent recipes
    recent_recipes = get_recent_recipes()
    # Show 3 recipes with highest votes
    highest_voted_recipe = get_votes_recipes()
    # Show 12 random recipes on recipe search that change when page refreshes
    recipes = get_random_recipes()
    # get categories, cuisines, allergens, difficulty for dropdown options
    categories = get_categories()
    cuisine = get_cuisine()
    allergens = get_allergens()
    difficulty = get_difficulty()
    return render_template("recipesearch.html",
                           test=mongo.db.test_collection.find(),
                           recipes=recipes,
                           categories=categories,
                           cuisine=cuisine,
                           allergens=allergens,
                           highestvotes=highest_voted_recipe,
                           recentrecipes=recent_recipes)


# FUNCTION :: GET RECIPES BY ANY VALUE - KEYWORDS HASHTAGS
@app.route('/recipesearchquery', methods=['POST', 'GET'])
def recipesearchquery():
    query = request.get_data()
    query = str(query)
    # remove b from search text
    query = query[1:]
    # remove quotes ' ' from either end of search text
    query = query.strip('\'"')
    filteredRecipes = None
    try:
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
                           {'$text': {'$search': query}})]
    except Exception as e:
        # print("error accessing DB to find category %s" % str(e))
        return render_template("500.html")

    if filteredRecipes:
        print("recipes by category exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that category found")
        message = "fail"
        return message


# FUNCTION :: GET RECIPES BY CATEGORY
@app.route('/filter_by_category/<category>', methods=['POST', 'GET'])
def filter_by_category(category):
    filteredRecipes = None
    category_name = category
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
                            {
                                '$query':
                                    {'category': category_name},
                                    '$orderby': {'votes': -1}
                             }
                           )]
    except Exception as e:
        # print("error accessing DB to find category %s" % str(e))
        return render_template("500.html")

    if filteredRecipes:
        print("recipes by category exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that category found")
        message = "fail"
        return message


# FUNCTION :: GET RECIPES BY CUISINE
@app.route('/filter_by_cuisine/<cuisine>', methods=['POST', 'GET'])
def filter_by_cuisine(cuisine):
    filteredRecipes = None
    cuisine_name = cuisine
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
                {'$query': {'cuisine': cuisine_name},
                    '$orderby': {'votes': -1}}
            )]
    except Exception as e:
        # print("error accessing DB to find cuisine %s" % str(e))
        return render_template("500.html")

    if filteredRecipes:
        print("recipes by cuisine exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that cuisine found")
        message = "fail"
        return message


# FUNCTION :: GET RECIPES WITHOUT THE SELECTED ALLERGEN
@app.route('/filter_by_allergen/<allergen>', methods=['POST', 'GET'])
def filter_by_allergen(allergen):
    filteredRecipes = None
    message = "fail"
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
                            {'allergens': {'$nin': [allergen]}}
                            )]
    except Exception as e:
        # print("error accessing DB to find allergen %s" % str(e))
        return message

    if filteredRecipes:
        print("recipes by allergen exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that allergen found")
        return message


# FUNCTION :: GET RECIPES BY MAIN INGREDIENT
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
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
            {'$query':
                {'main_ingredient': ingredient_name},
                '$orderby': {'votes': -1}}
            )]
    except Exception as e:
        # print("error accessing DB to find ingredient name %s" % str(e))
        return render_template("500.html")

    if filteredRecipes:
        print("recipes by ingredient exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that ingredient found")
        message = "fail"
        return message


# FUNCTION :: GET RECIPES BY CATEGORY & CUISINE
@app.route('/filter_by_catcuis/<category>/<cuisine>', methods=['POST', 'GET'])
def filter_by_catcuis(category, cuisine):
    filteredRecipes = None
    category_name = category
    cuisine_name = cuisine
    try:
        # Query recipes collection and return ordered by votes descending
        filteredRecipes = [recipe for recipe in mongo.db.recipes.find(
            {'$query': {'category': category_name, 'cuisine': cuisine_name},
             '$orderby': {'votes': -1}})]
    except:
        # print("error accessing DB to find allergen %s" % str(e))
        return render_template("500.html")

    if filteredRecipes:
        print("recipes by allergen exist")
        return render_template("resultTemplate.html",
                               reciperesults=filteredRecipes)
    else:
        print("no recipes with that allergen found")
        message = "fail"
        return message


# FUNCTION :: SIGN UP NEW USER / REGISTER / CREATE RECORD IN USERS COLLECTION
@app.route('/signup_user', methods=['POST'])
def signup_user():
    # query db to see if username already exists
    check_user = get_user(request.form.get('signupUsername'))
    # if that username is not in db then create and add new user
    if not check_user:
        users = mongo.db.users
        new_user = {
                'username': request.form.get('signupUsername').lower(),
                'hashed_password': generate_password_hash(
                                    request.form.get('signupPassword'),
                                    "sha256"),
                'firstname': request.form.get('firstName'),
                'lastname': request.form.get('lastName'),
                'recipe_votes': []
        }
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
    if user:
        check_password = compare_password(user['hashed_password'], pw)
        if check_password:
            # add username to flask session
            session['username'] = user['username']
            session['userid'] = str(user['_id'])  # ObjectId to str
            # set session isLoggedin to True: session is true
            session['isLoggedin'] = True
            # message to user
            message = "Welcome back, " + user['username'] + "." \
                + "<br />""You will be redirected to your MyRecipes page."
            id = str(user['_id'])
            response = {
                "username": user['username'], "_id": id, "message": message
                }
            return jsonify(response)
        elif not check_password:
            # wrong password
            returnvar = "1"
            return returnvar
    else:
        # no user by that username
        returnvar = "2"
        return returnvar
    return


# Error handling suggested by Sentdex on YouTube
@app.errorhandler(404)
def page_not_found(error):
    # 404 error is redirected to 404.html
    return render_template('404.html')


@app.errorhandler(500)
def internal_error(error):
    # 500 error is redirected to 500.html
    session.pop('_flashes', None)
    session.pop('username', None)
    return render_template('500.html')


# # PAGE :: GRAPHS
@app.route('/graphs')
def graphs():
    cuis_data = cuis_dataframe()
    cat_data = cat_dataframe()

    cat_data_dict = {}
    for k, v in cat_data.iteritems():
        cat_data_dict.update({k: v})

    cuis_data_dict = {}
    for k, v in cuis_data.iteritems():
        cuis_data_dict.update({k: v})
    return render_template("graphs.html",
                           cuis_data=cuis_data_dict,
                           cat_data=cat_data_dict)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)

# import pdb; pdb.set_trace()
