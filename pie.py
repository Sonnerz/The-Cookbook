import matplotlib.pyplot as plt
import pandas
import os
import re
import pymongo
import json
from flask import Flask, jsonify, json
from flask_pymongo import PyMongo

DBS_NAME = os.getenv("DBS_NAME")
MONGO_URI = os.getenv("MONGODB_URI")

app = Flask(__name__)
app.config["DBS_NAME"] = "cookbook"
app.config["MONGO_URI"] = "mongodb://localhost:27017/cookbook"
mongo = PyMongo(app)

RECIPES_DATA_PATH = 'static/data/recipes.json'
cuisine_list = mongo.db.cuisine.find()
category_list = mongo.db.categories.find()


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
    recipesCountsCatDataFrame = pandas.DataFrame()
    recipesCountsCatDataFrame['Recipe Category'] = [recipe['category'] for recipe in results]
    # recipesCountsCatDataFrame['Category Counts'] = recipesCountsCatDataFrame.groupby(['Recipe Category'])['Recipe Category'].transform('count')
    recipe_by_category = recipesCountsCatDataFrame['Recipe Category'].value_counts()
    # recipesCountsCatDataFrame.to_html('templates/graphscountscat_sub.html')
    return recipe_by_category

# TABLE OF COUNTS - CUISINE
def cuis_dataframe():
    recipesCountsCuisDataFrame = pandas.DataFrame()
    recipesCountsCuisDataFrame['Recipe Cuisine'] = [recipe['cuisine'] for recipe in results]
    # recipesCountsCuisDataFrame['Counts'] = recipesCountsCuisDataFrame.groupby(['Recipe Cuisine'])['Recipe Cuisine'].transform('count')
    recipe_by_cuisine = recipesCountsCuisDataFrame['Recipe Cuisine'].value_counts()
    # recipesCountsCuisDataFrame.to_html('templates/graphscountscuis_sub.html')
    return recipe_by_cuisine


# TOP CUISINE PIE CHART
recipesDataFrame = pandas.DataFrame()
recipesDataFrame['cuisine'] = [recipe['cuisine'] for recipe in results]
for c in cuisine_list:
    recipesDataFrame[c['cuisine_name']] = recipesDataFrame['cuisine'].apply(lambda recipe: is_text_in_field(c['cuisine_name'], recipe))

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
    activities = ["French","Italian","No-Cuisine","Indian","American","Malaysian","Japanese","Thai","Chinese"]
    cols = ['c','m','r','b','indigo','tan','lime','y','teal']

    plt.pie(slices, colors=cols, labels=activities, 
            startangle=90, shadow=True, explode=(0,0,0,0,0,0,0,0,0.3), autopct='%1.1f%%')

    plt.title('Recipe Incidence of cuisine')
    fig.savefig('static/img/graphs/piechart.svg')


# TOP CATEGORY PIE CHART
recipesDataFrameCat = pandas.DataFrame()
recipesDataFrameCat['category'] = [recipe['category'] for recipe in results]
for c in category_list:
    recipesDataFrameCat[c['category_name']] = recipesDataFrameCat['category'].apply(lambda recipe: is_text_in_field(c['category_name'], recipe))


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
    activities = ["Chicken","Beef","Desserts","Vegetarian","Seafood","Pasta","Pork","Breakfast","Lunch","Baking"]
    cols = ['c','m','r','b','indigo','tan','teal','k','y','g']

    plt.pie(slices, colors=cols, labels=activities, 
            startangle=90, shadow=True, explode=(0.3,0,0,0,0,0,0,0,0,0), autopct='%1.1f%%')

    plt.title('Recipe Incidence of Category')
    fig.savefig('static/img/graphs/piechart-category.svg')
    # plt.show()


# region BAR CHARTS
# BAR CHARTS - CATEGORY
fig = plt.figure()
fig.subplots_adjust()

ax1 = fig.add_subplot(2,1,1)

ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)
ax1.set_xlabel('Category', fontsize=12)
ax1.set_ylabel('Number of recipes', fontsize=12)
ax1.xaxis.label.set_color('#666666')
ax1.yaxis.label.set_color('#666666')
ax1.tick_params(axis='x', colors='#666666')
ax1.tick_params(axis='y', colors='#666666')
ax1.set_title('Top 10 Category', fontsize=15, color='#666666')

#plot the top 10 Category
recipe_by_category = cat_dataframe()
recipe_by_category[:10].plot(ax=ax1, kind='bar', color='#FF7A00')

#colour the spines(borders)
for spine in ax1.spines.values():
    spine.set_edgecolor('#666666')

#render the graph
# plt.show()

# Save the figure
fig.savefig('static/img/graphs/barchart-category.svg')



# BAR CHARTS - CUISINE
fig = plt.figure()
fig.subplots_adjust(hspace=.9)

ax1 = fig.add_subplot(2,1,1)

ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)
ax1.set_xlabel('Cuisine', fontsize=12)
ax1.set_ylabel('Number of recipes', fontsize=12)
ax1.xaxis.label.set_color('#666666')
ax1.yaxis.label.set_color('#666666')
ax1.tick_params(axis='x', colors='#666666')
ax1.tick_params(axis='y', colors='#666666')
ax1.set_title('Top 10 Cuisine', fontsize=15, color='#666666')

#plot the top 10 Cuisine
recipe_by_cuisine = cuis_dataframe()
recipe_by_cuisine[:10].plot(ax=ax1, kind='bar', color='#FF7A00')

#colour the spines(borders)
for spine in ax1.spines.values():
    spine.set_edgecolor('#666666')

#render the two graphs at once
# plt.show()

# Save the figure
fig.savefig('static/img/graphs/barchart-cuisine.svg')

# endregion




# RUN FUNCTIONS
cat_dataframe()
cuis_dataframe()
category_pie()
cuisine_pie()


