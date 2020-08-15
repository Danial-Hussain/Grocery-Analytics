# Import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import requests as rq
import json
import os
import time
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from product import Product
from product import Base
import urllib.request


def get_categories(categories):
	# Get categories
	driver.get(BASEURL)
	driver.implicitly_wait(10)
	# Expand all categories
	driver.find_elements_by_css_selector(".Radio-Root--3rL7F~ .ShowMore-Action--zkWk7")[0].click()
	# Gather categories
	category_choices = driver.find_elements_by_css_selector(".Radio-Label--1a5oe")
	# Store categories in a list
	cat_names = [cat.text for cat in category_choices]
	# Unwanted categories
	unwanted = ["Body Care", 'Beauty', 'Floral']
	# Remove unwanted categories from list
	cat_names = [ele for ele in cat_names if ele not in unwanted]
	for category in cat_names:
		new_cat = str(category)
		new_cat = new_cat.replace("& ", "")
		new_cat = new_cat.replace(",", "")
		new_cat = new_cat.replace(" ", "-")
		categories[category] = [BASEURL + "&category={}".format(new_cat.lower()), new_cat.lower()]
	# Save the newly collected data in a json file titled categories
	with open('data/categories.json', 'w') as fp:
		json.dump(categories, fp, indent = 4)


def get_subcategories(categories):
	for category in categories:
		# Get the url for the category
		url = categories[category][0]
		# Open that url
		driver.get(url)
		driver.implicitly_wait(10)
		# See if the show more button appears
		show_More = driver.find_elements_by_css_selector(".Radio-Root--3rL7F~ .ShowMore-Action--zkWk7")
		if len(show_More) > 0:
			show_More[0].click()
		# Get the subcategories
		subcategory_choices = driver.find_elements_by_css_selector(".Filters-StyledCheckbox--oaCnA+ .Filters-StyledCheckbox--oaCnA .Radio-Label--1a5oe")
		# Get the name of the subcategories
		sub_names = [sub.text for sub in subcategory_choices]
		# A dictionary to hold the subcategories for a category
		tmp_dic = {}
		for name in sub_names:
			new_sub = str(name)
			new_sub = new_sub.replace("& ", "")
			new_sub = new_sub.replace(",", "")
			new_sub = new_sub.replace(" ", "-")
			tmp_dic[name] = url + "&subcategory=" + categories[category][1] + ".{}".format(new_sub.lower())

		# Replace the current value for the category with a dictionary of the subcategories
		categories[category] = [tmp_dic]
	# Save the newly collected data in a json file titled subcategories
	with open('data/subcategories.json', 'w') as fp:
		json.dump(categories, fp, indent = 4)


def get_products(categories):
	# Loop through all the categories
	for category in categories:
		# Loop through all the subcategories
		for subcategory in categories[category][0]:
			# Url for the subcategory
			tmp = categories[category][0][subcategory]
			# Get the url
			driver.get(tmp)
			# Scroll to the bottom of page 
			lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
			match=False
			while(match==False):
				lastCount = lenOfPage
				time.sleep(2)
				lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
				if lastCount==lenOfPage:
					match=True
			# Get the products
			products = driver.find_elements_by_css_selector(".ProductCard-Root--3g5WI")
			# Get the links of the products
			links = [el.get_attribute("href") for el in products]
			# Set the key of the subcategory to the links of the products within that subcategory
			categories[category][0][subcategory] = links
	# Save the newly collected data in a json file titled products
	with open('data/products.json', 'w') as fp:
		json.dump(categories, fp, indent = 4)


def load_to_database(categories, SQLALCHEMY_DATABASE_URL):
	# Open json file that has all the data collected from the previous functions
	with open(os.getcwd()+"\\data\\products.json") as f:
		categories = json.load(f)
	# Variables to store quantity of invalid products, products without nutrition information, and products wihtout image
	invalid, no_nutrition, no_image = 0, 0, 0
	# Create SQL Database engine
	engine = create_engine(SQLALCHEMY_DATABASE_URL, echo = True)
	Base.metadata.create_all(bind=engine)
	Session = sessionmaker(bind = engine)
	# Create session
	session = Session()
	# Loop over each category
	for category in categories:
		# Loop over each subcategory
		for subcategory in categories[category][0]:
			# List of product urls for the subcategory
			urls = categories[category][0][subcategory]
			# Each product url
			for url in urls:
				# Get that product's url and scrape its data
				driver.get(url)
				time.sleep(2)
				# Check if nutrition info is available, otherwise go to next product
				try:
					if driver.find_elements_by_css_selector(".Collapsible-Root--3cwwH+ .Collapsible-Root--3cwwH .Collapsible-Title--30gLK") != []:
						driver.find_elements_by_css_selector(".Collapsible-Root--3cwwH+ .Collapsible-Root--3cwwH .Collapsible-Title--30gLK")[0].click()
					else:
						driver.find_elements_by_css_selector(".Collapsible-Title--30gLK")[0].click()
					time.sleep(1)
				except:
					print("Product doesn't have nutrition info")
					no_nutrition += 1
				# Try to get product name
				try:
					p_name = driver.find_elements_by_css_selector(".ProductHeader-Name--1ysBV")[0].text
				except:
					continue
					invalid += 1
				# Try to get the serving size
				try:
					serving_size = driver.find_elements_by_css_selector(".Separator__3rdE_+ .NutritionTable-Unbreakable--1UPcX")[0].text
				except: 
					serving_size = "None"
				# Get the text from nutrition table
				try:
					values = driver.find_elements_by_css_selector(".NutritionTable-Root--YcoZx")[0].text
					values = str.join(" ", values.splitlines())
				except:
					print("No nutrition")
				# Extract nutrition information
				try:
					if re.findall(r"(?<=Total Fat )[\d\|.]+", values) != []:
						tot_fat = re.findall(r"(?<=Total Fat )[\d\|.]+", values)[0]
						tot_fat = float(tot_fat)
					else:
						tot_fat = None

					if re.findall(r"(?<=Cholesterol )[\d\|.]+", values) != []:
						tot_cholesterol = re.findall(r"(?<=Cholesterol )[\d\|.]+", values)[0]
						tot_cholesterol = float(tot_cholesterol) 
					else:
						tot_cholesterol = None

					if re.findall(r"(?<=Protein )[\d\|.]+", values) != []:
						tot_protein = re.findall(r"(?<=Protein )[\d\|.]+", values)[0]
						tot_protein = float(tot_protein)
					else:
						tot_protein = None

					if re.findall(r"(?<=Total Carbohydrates )[\d\|.]+", values) != []:
						tot_carbs = re.findall(r"(?<=Total Carbohydrates )[\d\|.]+", values)[0]
						tot_carbs = float(tot_carbs)
					else:
						tot_carbs = None

					if re.findall(r"(?<=Calories )[\d\|.]+", values) != []:
						tot_calories = re.findall(r"(?<=Calories )[\d\|.]+", values)[0]
						tot_calories = float(tot_calories)
					else:
						tot_calories = None
				except:
					tot_fat = None
					tot_calories = None
					tot_carbs = None
					tot_protein = None
					tot_cholesterol = None

				try:
					img = driver.find_elements_by_css_selector(".ImagePreviewer-Thumbnail--lEL4J:nth-child(1)")[0].get_attribute('style')
					img = img.split('url("')[1].split("\");")[0]
					blobData = get_blob(img)
				except:
					blobData = None
					no_image +=1

				# Create a new Product
				product = Product(
					category = category,
					subcategory = subcategory,
					name = p_name,
					serving = serving_size,
					calories = tot_calories,
					fat = tot_fat,
					carbohydrates = tot_carbs,
					protein = tot_protein,
					cholesterol = tot_cholesterol,
					image = blobData,
					url = url
					)

				# Add the product to the database
				session.add(product)
				
	#Commit additions
	session.commit()
	#Close session
	session.close()
	print("The number of invalid products: {}\n".format(invalid))
	print('The number of products without nutrition information {}\n'.format(no_nutrition))
	print('The number of products without images is {}\n'.format(no_image))


def get_blob(URL):
	# Open url and save to file
	with urllib.request.urlopen(URL) as url:
	  with open('temp.jpg', 'wb') as f:
	  	f.write(url.read())
	#Read file data
	with open('temp.jpg', 'rb') as file:
		blobData = file.read()
	# Remove file
	os.remove('temp.jpg')
	# Return blob data
	return blobData


if __name__ == "__main__":
	# Gets the latest version of chrome driver and caches it
	driver = webdriver.Chrome(ChromeDriverManager().install())
	BASEURL = "https://products.wholefoodsmarket.com/search?sort=relevance"

	# Store category names with their links
	categories = {}

	# SQL Alchemy database
	SQLALCHEMY_DATABASE_URL = "sqlite:///./data/product_data.db"

	# Get the categories of products
	get_categories(categories)

	# Get the subcategories of products
	get_subcategories(categories)

	# Get the products
	get_products(categories)

	# Load the data to the database
	load_to_database(categories, SQLALCHEMY_DATABASE_URL)

	# End the driver session
	driver.quit()