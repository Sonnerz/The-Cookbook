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


def is_text_in_field(token, text):
    token = token.lower()
    text = ''.join(text).lower()
    match = re.search(token, text)
    if match:
        return True
    return False


results = read_json(RECIPES_DATA_PATH)

recipesDataFrame = pandas.DataFrame()
# recipesDataFrame['description'] = [recipe['description'] for recipe in results]
recipesDataFrame['cuisine'] = [recipe['cuisine'] for recipe in results]

# recipesDataFrame['tarts'] = recipesDataFrame['description'].apply(lambda recipe: is_text_in_field('tarts', recipe))
recipesDataFrame['Chinese'] = recipesDataFrame['cuisine'].apply(lambda recipe: is_text_in_field('Chinese', recipe))
recipesDataFrame['Italian'] = recipesDataFrame['cuisine'].apply(lambda recipe: is_text_in_field('Italian', recipe))
recipesDataFrame['American'] = recipesDataFrame['cuisine'].apply(lambda recipe: is_text_in_field('American', recipe))

# print(recipesDataFrame['tarts'].value_counts()[True])
print(recipesDataFrame['Chinese'].value_counts()[True])
print(recipesDataFrame['Italian'].value_counts()[True])
print(recipesDataFrame['American'].value_counts()[True])




def cuisine_pie():
    slices = recipesDataFrame['Chinese'].value_counts()[True], recipesDataFrame['Italian'].value_counts()[True], recipesDataFrame['American'].value_counts()[True]

    activities = ['Chinese', 'Italian', 'American']
    cols = ['c','b','a']
    
    plt.pie(slices, colors=cols, labels=activities, 
            startangle=90, shadow=True, explode=None, autopct='%1.1f%%')
            
    plt.title('Recipe Incidence\nof cuisine')
    plt.show()
    

cuisine_pie()





