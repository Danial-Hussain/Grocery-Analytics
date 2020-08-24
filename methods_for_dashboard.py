import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import Franklin_Gothic_Book

conn = sqlite3.connect('data/product_data.db', check_same_thread=False)

c = conn.cursor()


def getTotals(cart):
	if cart == []:
		return None, None, None, None, None

	# Total Calories
	tot_cal = 0
	# Total Fat
	tot_fat = 0
	# Total Carbohydrates
	tot_carb = 0
	# Total Protein
	tot_prot = 0 
	# Total Cholesterol
	tot_chol = 0

	for item in cart:
		cal = c.execute("SELECT calories FROM product WHERE name = (?)", (item,)).fetchone()[0]
		fat = c.execute("SELECT fat FROM product WHERE name = (?)", (item,)).fetchone()[0]
		carb = c.execute("SELECT carbohydrates FROM product WHERE name = (?)", (item,)).fetchone()[0]
		prot = c.execute("SELECT protein FROM product WHERE name = (?)", (item,)).fetchone()[0]
		chol = c.execute("SELECT cholesterol FROM product WHERE name = (?)", (item,)).fetchone()[0]
		if cal != None: tot_cal += cal
		if fat != None:  tot_fat += fat
		if carb != None: tot_carb += carb
		if prot != None: tot_prot += prot 
		if chol != None: tot_chol += chol 

	return tot_cal, tot_fat, tot_carb, tot_prot, tot_chol


def createBarChart(cart):
	if cart == []:
		return None

	data = {'calories': [], 'fat': [], 'carbohydrates': [], 'protein': [], 'cholesterol': [],
			'avg_calories': [], 'avg_fat': [], 'avg_carbohydrates': [], 'avg_protein': [], 'avg_cholesterol': [], 'subcategory': []}
	ind = []

	for item in cart:
		cal = c.execute("SELECT calories FROM product WHERE name = (?)", (item,)).fetchone()[0]
		fat = c.execute("SELECT fat FROM product WHERE name = (?)", (item,)).fetchone()[0]
		carb = c.execute("SELECT carbohydrates FROM product WHERE name = (?)", (item,)).fetchone()[0]
		prot = c.execute("SELECT protein FROM product WHERE name = (?)", (item,)).fetchone()[0]
		chol = c.execute("SELECT cholesterol FROM product WHERE name = (?)", (item,)).fetchone()[0]

		subcat = c.execute("SELECT subcategory FROM product WHERE name = (?)", (item,)).fetchone()[0]
		avg_cal = c.execute("SELECT AVG(calories) FROM product WHERE subcategory = (?)", (subcat,)).fetchone()[0]
		avg_fat = c.execute("SELECT AVG(fat) FROM product WHERE subcategory = (?)", (subcat,)).fetchone()[0]
		avg_carb = c.execute("SELECT AVG(carbohydrates) FROM product WHERE subcategory = (?)", (subcat,)).fetchone()[0]
		avg_prot = c.execute("SELECT AVG(protein) FROM product WHERE subcategory = (?)", (subcat,)).fetchone()[0]
		avg_chol = c.execute("SELECT AVG(cholesterol) FROM product WHERE subcategory = (?)", (subcat,)).fetchone()[0]

		ind.append(item)
		data['calories'].append(cal)
		data['fat'].append(fat)
		data['carbohydrates'].append(carb)
		data['protein'].append(prot)
		data['cholesterol'].append(chol)
		data['avg_calories'].append(avg_cal)
		data['avg_fat'].append(avg_fat)
		data['avg_carbohydrates'].append(avg_carb)
		data['avg_protein'].append(avg_prot)
		data['avg_cholesterol'].append(avg_chol)
		data['subcategory'].append(subcat)


	df = pd.DataFrame(data = data, index = ind)
	imgs = []

	for i in range(len(cart)):
		fig, ax = plt.subplots()

		N = 5
		actual_vals = df.iloc[i, 0:5].values
		avg_vals = df.iloc[i, 5:10].values

		ind = np.arange(N)
		width = 0.3
		p1 = ax.bar(ind, actual_vals, width)
		p2 = ax.bar(ind+width, avg_vals, width)

		ax.set_title('Nutrition Information: {} versus {} products'.format(df.index[i], df.iloc[i, 10]), fontsize = 10)

		ax.set_xticks(ind+width / 2)
		ax.set_xticklabels(('Calories', 'Fat', 'Carbohydrates', 'Protein', 'Cholesterol'))

		ax.legend((p1[0], p2[0]), ('{}'.format(df.index[i]), 'Average for {}'.format(df.iloc[i, 10])))

		i+=1

		plt.savefig('static/bar{}.png'.format(i))

	return imgs
