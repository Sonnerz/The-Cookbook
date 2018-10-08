import matplotlib
import matplotlib.pyplot as plt
import pandas
import os
import re
import pymongo
import json
from flask import Flask, jsonify, json
from flask_pymongo import PyMongo
matplotlib.use('Agg')

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

statistics = Flask(__name__)
statistics.debug = False

if statistics.debug:
    statistics.config["DBS_NAME"] = "cookbook"
    statistics.config["MONGO_URI"] = "mongodb://localhost:27017/cookbook"
else:
    statistics.config["DBS_NAME"] = DBS_NAME
    statistics.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(statistics)

RECIPES_DATA_PATH = 'static/data/recipes.json'
cuisine_list = mongo.db.cuisine.find()
category_list = mongo.db.categories.find()
allergen_list = mongo.db.allergens.find()


# READ JSON FILE
def read_json(file_path):
    results = []
    with open(RECIPES_DATA_PATH) as recipes_file:
        for recipes in recipes_file:
            try:
                recipe = json.loads(recipes)
                results.append(recipe)
            except ValueError:
                pass
        return results


# SEARCH JSON FOR TEXT
def is_text_in_field(token, recipe_content):
    token = token.lower()
    recipe_content = ''.join(recipe_content).lower()
    match = re.search(token, recipe_content)
    if match:
        return True
    return False

results = read_json(RECIPES_DATA_PATH)


# TABLE OF COUNTS - CATEGORY
def cat_dataframe():
    recipesCatDataFrame = pandas.DataFrame()
    recipesCatDataFrame['Recipe Category'] = [recipe['category']
                                              for recipe in results]
    recipe_by_category = recipesCatDataFrame['Recipe Category'].value_counts()
    return recipe_by_category


# TABLE OF COUNTS - CUISINE
def cuis_dataframe():
    recipesCuisDataFrame = pandas.DataFrame()
    recipesCuisDataFrame['Recipe Cuisine'] = [recipe['cuisine']
                                              for recipe in results]
    recipe_by_cuisine = recipesCuisDataFrame['Recipe Cuisine'].value_counts()
    return recipe_by_cuisine


# TOP CUISINE PIE CHART
recipesDataFrame = pandas.DataFrame()
recipesDataFrame['cuisine'] = [recipe['cuisine'] for recipe in results]
for c in cuisine_list:
    recipesDataFrame[
        c['cuisine_name']] = recipesDataFrame['cuisine'] \
        .apply(lambda recipe: is_text_in_field(c['cuisine_name'], recipe))


def cuisine_pie():
    fig = plt.figure()
    slices = recipesDataFrame['French'].value_counts()[True],\
        recipesDataFrame['Italian'].value_counts()[True],\
        recipesDataFrame['No-Cuisine'].value_counts()[True],\
        recipesDataFrame['Indian'].value_counts()[True],\
        recipesDataFrame['American'].value_counts()[True],\
        recipesDataFrame['Malaysian'].value_counts()[True],\
        recipesDataFrame['Japanese'].value_counts()[True],\
        recipesDataFrame['Thai'].value_counts()[True],\
        recipesDataFrame['Chinese'].value_counts()[True]
    activities = ["French", "Italian", "No-Cuisine", "Indian",
                  "American", "Malaysian", "Japanese", "Thai", "Chinese"]
    cols = ['c', 'm', 'r', 'b', 'indigo', 'tan', 'lime', 'y', 'teal']

    plt.pie(slices, colors=cols, labels=activities,
            startangle=90, shadow=True, explode=(0.2, 0, 0.5, 0, 0.2, 0, 0.2,
                                                 0, 0.3), autopct='%1.1f%%')

    fig.savefig('static/img/graphs/piechart.svg')
    # plt.show()


# TOP CATEGORY PIE CHART
recipesDataFrameCat = pandas.DataFrame()
recipesDataFrameCat['category'] = [recipe['category'] for recipe in results]
for c in category_list:
    recipesDataFrameCat[
        c['category_name']] = recipesDataFrameCat['category'].apply(
            lambda recipe: is_text_in_field(c['category_name'], recipe))


def category_pie():
    fig = plt.figure()
    slices = recipesDataFrameCat['Chicken'].value_counts()[True],\
        recipesDataFrameCat['Beef'].value_counts()[True],\
        recipesDataFrameCat['Desserts'].value_counts()[True],\
        recipesDataFrameCat['Vegetarian'].value_counts()[True],\
        recipesDataFrameCat['Seafood'].value_counts()[True],\
        recipesDataFrameCat['Pasta'].value_counts()[True],\
        recipesDataFrameCat['Pork'].value_counts()[True],\
        recipesDataFrameCat['Breakfast'].value_counts()[True],\
        recipesDataFrameCat['Lunch'].value_counts()[True],\
        recipesDataFrameCat['Baking'].value_counts()[True]
    activities = ["Chicken", "Beef", "Desserts", "Vegetarian", "Seafood",
                  "Pasta", "Pork", "Breakfast", "Lunch", "Baking"]
    cols = ['c', 'm', 'r', 'b', 'indigo', 'tan', 'teal', 'k', 'y', 'g']

    plt.pie(slices, colors=cols, labels=activities,
            startangle=90, shadow=True, explode=(0.3, 0, 0.2, 0, 0, 0, 0.3, 0,
                                                 0.4, 0), autopct='%1.1f%%')

    fig.savefig('static/img/graphs/piechart-category.svg')
    # plt.show()


# ALLERGEN PIE CHART
recipesDataFrameAll = pandas.DataFrame()
recipesDataFrameAll['allergen'] = [recipe['allergens'] for recipe in results]
for a in allergen_list:
    recipesDataFrameAll[
        a['allergen_name']] = recipesDataFrameAll['allergen'].apply(
            lambda recipe: is_text_in_field(a['allergen_name'], recipe))


def allergen_pie():
    fig = plt.figure()
    slices = recipesDataFrameAll['Gluten'].value_counts()[True],\
        recipesDataFrameAll['Eggs'].value_counts()[True],\
        recipesDataFrameAll['Fish'].value_counts()[True],\
        recipesDataFrameAll['Peanuts'].value_counts()[True],\
        recipesDataFrameAll['Soybeans'].value_counts()[True],\
        recipesDataFrameAll['Milk'].value_counts()[True],\
        recipesDataFrameAll['Tree nuts'].value_counts()[True],\
        recipesDataFrameAll['Celery'].value_counts()[True],\
        recipesDataFrameAll['Sulphites'].value_counts()[True],\
        recipesDataFrameAll['Molluscs'].value_counts()[True],\
        recipesDataFrameAll['Crustaceans'].value_counts()[True],\
        recipesDataFrameAll['Sesame seeds'].value_counts()[True]
    activities = ["Gluten", "Eggs", "Fish", "Peanuts", "Soybeans", "Milk",
                  "Tree nuts", "Celery", "Sulphites", "Molluscs",
                  "Crustaceans", "Sesame seeds"]
    cols = ['c', 'm', 'y', 'g', 'b', 'r', 'teal', 'indigo',
            'tan', 'teal', 'c', 'g']

    plt.pie(slices, colors=cols, labels=activities, startangle=90,
            shadow=True, explode=(0.2, 0, 0, 0.3, 0, 0, 0.3, 0, 0,
                                  0.3, 0, 0), autopct='%1.1f%%')

    fig.savefig('static/img/graphs/piechart-allergen.svg')
    # plt.show()


# region BAR CHARTS


# BAR CHARTS - CATEGORY
fig = plt.figure()
fig.subplots_adjust()

ax1 = fig.add_subplot(2, 1, 1)

ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)
ax1.set_xlabel('Category', fontsize=12)
ax1.set_ylabel('Number of recipes', fontsize=12)
ax1.xaxis.label.set_color('#393d3f')
ax1.yaxis.label.set_color('#393d3f')
ax1.tick_params(axis='x', colors='#393d3f')
ax1.tick_params(axis='y', colors='#393d3f')
ax1.set_title('Top 10 Categories', fontsize=15, color='#393d3f')

# plot the top 10 Category
recipe_by_category = cat_dataframe()
recipe_by_category[:10].plot(ax=ax1, kind='bar', color='#586a7a')

# colour the spines(borders)
for spine in ax1.spines.values():
    spine.set_edgecolor('#393d3f')

# render the graph
# plt.show()

# Save the figure
fig.savefig('static/img/graphs/barchart-category.svg')


# BAR CHARTS - CUISINE
fig1 = plt.figure()
fig1.subplots_adjust()

ax2 = fig1.add_subplot(2, 1, 1)

ax2.tick_params(axis='x', labelsize=15)
ax2.tick_params(axis='y', labelsize=15)
ax2.set_xlabel('Cuisine', fontsize=12)
ax2.set_ylabel('Number of recipes', fontsize=12)
ax2.xaxis.label.set_color('#393d3f')
ax2.yaxis.label.set_color('#393d3f')
ax2.tick_params(axis='x', colors='#393d3f')
ax2.tick_params(axis='y', colors='#393d3f')
ax2.set_title('Top Cuisine', fontsize=15, color='#393d3f')

# plot the top 10 Cuisine
recipe_by_cuisine = cuis_dataframe()
recipe_by_cuisine[:10].plot(ax=ax2, kind='bar', color='#62929e')

# colour the spines(borders)
for spine in ax2.spines.values():
    spine.set_edgecolor('#393d3f')

# render the two graphs at once
# plt.show()

# Save the figure
fig1.savefig('static/img/graphs/barchart-cuisine.svg')

# endregion


# RUN FUNCTIONS
cat_dataframe()
cuis_dataframe()
category_pie()
cuisine_pie()
allergen_pie()
