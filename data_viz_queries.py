import sqlite3
import pandas as pd

conn = sqlite3.connect('data/product_data.db')

c = conn.cursor()

# Creating average_for_categories.csv file
categories = c.execute("SELECT DISTINCT category FROM product").fetchall()
categories = [val[0] for val in categories]
data = {'Calories': [], 'Fat': [], 'Carbohydrates': [], 'Protein': []}

for val in categories:
	value = val
	cal = c.execute("SELECT AVG(calories) FROM product WHERE category = (?)", (value,)).fetchone()[0]
	fat = c.execute("SELECT AVG(fat) FROM product WHERE category = (?)", (value,)).fetchone()[0]
	carb = c.execute("SELECT AVG(carbohydrates) FROM product WHERE category = (?)", (value,)).fetchone()[0]
	prot = c.execute("SELECT AVG(protein) FROM product WHERE category = (?)", (value,)).fetchone()[0]
	data['Calories'].append(cal)
	data['Fat'].append(fat)
	data['Carbohydrates'].append(carb)
	data['Protein'].append(prot)

df = pd.DataFrame(data = data, index = categories)
df.to_csv(r'data\average_for_categories.csv', index = True)


# Creating most_prot-carb-fat csv file
protein = c.execute("SELECT * FROM (SELECT name, protein FROM product ORDER BY protein DESC) LIMIT 10").fetchall()
carbohydrates = c.execute("SELECT * FROM (SELECT name, carbohydrates FROM product ORDER BY carbohydrates DESC) LIMIT 10").fetchall()
fat = c.execute("SELECT * FROM (SELECT name, fat FROM product ORDER BY fat DESC) LIMIT 10").fetchall()

prot = pd.DataFrame(data = {i[0] : i[1] for i in protein}, index= ["Protein"]).T
carb = pd.DataFrame(data = {i[0] : i[1] for i in carbohydrates}, index = ["Carbohydrates"]).T
fat = pd.DataFrame(data = {i[0] : i[1] for i in fat}, index = ["Fat"]).T
tot_data = prot.append([carb, fat])

tot_data.to_csv(r'data\most_prot-carb-fat.csv', index = True)
