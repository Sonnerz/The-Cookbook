import matplotlib.pyplot as plt
import json
import pandas

RECIPES_DATA_PATH = 'static/data/recipes.json'

results=[]
with open(RECIPES_DATA_PATH) as recipes_file:
    for recipe in recipes_file:
        try:
            rec = json.loads(recipe)
            results.append(rec)
        except ValueError:
            pass
        

#create a DataFrame
recipesDataFrame = pandas.DataFrame()
recipesDataFrame['Recipe name'] = [recipe['name'] for recipe in results]
recipesDataFrame['Recipe Category'] = [recipe['category'] for recipe in results]
recipesDataFrame['Recipe Cuisine'] = [recipe['cuisine'] for recipe in results]
recipesDataFrame['Votes'] = [recipe['votes'] for recipe in results]

# recipesDataFrame.sort_values('votes')
print(recipesDataFrame)
recipesDataFrame.to_html()

# print(recipesDataFrame.head())


recipe_by_cuisine = recipesDataFrame['cuisine'].value_counts()
recipe_by_category = recipesDataFrame['category'].value_counts()

print(recipe_by_cuisine.head())
print(recipe_by_category.head())

# recipesDataFrame.to_html('templates/graphs_sub.html')

#create our drawing space (figure)
fig = plt.figure()
fig.subplots_adjust(hspace=.9)

#prepare to plot two charts on teh same figure
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)

#style the axes
ax1.tick_params(axis='x', labelsize=15)
ax1.tick_params(axis='y', labelsize=15)
ax1.set_xlabel('Recipe Cuisine', fontsize=15)
ax1.set_ylabel('Number of recipes', fontsize=15)
ax1.xaxis.label.set_color('#666666')
ax1.yaxis.label.set_color('#666666')
ax1.tick_params(axis='x', colors='#666666')
ax1.tick_params(axis='y', colors='#666666')
#style the title 
ax1.set_title('Top 10 cuisine', fontsize=15, color='#666666')

#plot the top 10 tweet languages and appearance count using a bar chart
recipe_by_cuisine[:10].plot(ax=ax1, kind='bar', color='#FF7A00')

#coolor the spines(borders)
for spine in ax1.spines.values():
    spine.set_edgecolor('#666666')
    
    
#second subplot
ax2.tick_params(axis='x', labelsize=15)
ax2.tick_params(axis='y', labelsize=15)
ax2.set_xlabel('Countries', fontsize=15)
ax2.set_ylabel('Number of Tweets', fontsize=15)
ax2.xaxis.label.set_color('#666666')
ax2.yaxis.label.set_color('#666666')
ax2.tick_params(axis='x', colors='#666666')
ax2.tick_params(axis='y', colors='#666666')
#style the title 
ax2.set_title('Top 10 countries', fontsize=15, color='#666666')

#plot the top 10 tweet languages and appearance count using a bar chart
recipe_by_category[:10].plot(ax=ax2, kind='bar', color='#FF7A00')

#coolor the spines(borders)
for spine in ax2.spines.values():
    spine.set_edgecolor('#666666')
    
#render the two graphs at once
# plt.show()
fig.savefig('sine_wave_plot.svg')