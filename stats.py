# %matplotlib notebook
import matplotlib.pyplot as plt
import json

RECIPES_DATA_PATH = 'recipes.json'

results = []
# with open(RECIPES_DATA_PATH) as recipes_file:
with open('recipes.json') as recipes_file:
    for recipe in recipes_file:
        try:
            status = json.loads(recipe)
            results.append(status)
        except ValueError:
            pass
print(len(results))


