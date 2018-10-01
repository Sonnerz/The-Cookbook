# %matplotlib notebook
import matplotlib.pyplot as plt
import json
import re
import pandas

RECIPES_DATA_PATH = 'static/data/recipes.json'

def read_json(file_path):
    results = []
    with open(RECIPES_DATA_PATH) as recipes_file:
        for recipes in recipes_file:
            try:
                recipe = json.loads(recipes)
                results.append(recipe)
            except ValueError:
                pass
        print(len(results))
        return results


def is_text_in_description(token, text):
    token = token.lower()
    text = ''.join(text).lower()
    match = re.search(token, text)
    if match:
        return True
    return False


results = read_json(RECIPES_DATA_PATH)
recipesDataFrame = pandas.DataFrame()
recipesDataFrame['description'] = [recipe['description'] for recipe in results]

recipesDataFrame['tarts'] = recipesDataFrame['description'].apply(lambda recipe: is_text_in_description('tarts', recipe))

print(recipesDataFrame['tarts'].value_counts()[True])






