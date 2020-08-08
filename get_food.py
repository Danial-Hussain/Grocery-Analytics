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


def load_to_database(categories):
	# Open json file that has all the data collected from the previous functions
	with open(os.getcwd()+"\\data\\products.json") as f:
		categories = json.load(f)
	# Create SQL Database engine
	engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
					driver.find_elements_by_css_selector(".Collapsible-Root--3cwwH+ .Collapsible-Root--3cwwH .Collapsible-Title--30gLK")[0].click()
					time.sleep(1)
				except:
					print("Product doesn't have nutrition info")
				
				try:
					p_name = driver.find_elements_by_css_selector(".ProductHeader-Name--1ysBV")[0].text
				except:
					continue

				try:
					serving_size = driver.find_elements_by_css_selector(".Separator__3rdE_+ .NutritionTable-Unbreakable--1UPcX")[0].text
				except: 
					serving_size = None
				
				try:
					values = driver.find_elements_by_css_selector(".NutritionTable-Root--YcoZx")[0].text
					values = str.join(" ", values.splitlines())
				except:
					print("No nutrition")

				try:
					tot_fat = re.findall(r"(?<=Total Fat )[\d\|.]+", values)[0]
				except:
					tot_fat = None

				try:
					tot_cholesterol = re.findall(r"(?<=Cholesterol )[\d\|.]+", values)[0]
				except:
					tot_cholesterol = None

				try:
					tot_protein = re.findall(r"(?<=Protein )[\d\|.]+", values)[0]
				except: 
					tot_protein = None

				try:
					tot_carbs = re.findall(r"(?<=Total Carbohydrates )[\d\|.]+", values)[0]
				except:
					tot_carbs = None

				try:
					tot_calories = re.findall(r"(?<=Calories )[\d\|.]+", values)[0]
				except:
					tot_calories = None
				try:
					img = driver.find_elements_by_css_selector(".ImagePreviewer-Thumbnail--lEL4J:nth-child(1)")[0].get_attribute('style')
					img = img.split('url("')[1].split("\");")[0]
					blobData = get_blob(img)
				except:
					blobData = None

				# Create a new Product
				product = Product(
					category = category,
					subcategory = subcategory,
					name = p_name,
					serving = serving_size,
					calories = float(tot_calories),
					fat = float(tot_fat),
					carbohydrates = float(tot_carbs),
					protein = float(tot_protein),
					cholesterol = float(tot_cholesterol),
					image = float(blobData)
					)

				# Add the product to the database
				session.add(product)
				print(product)

	#Close session
	session.close()

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
	#get_categories()

	# Get the subcategories of products
	#get_subcategories()

	# Get the products
	#get_products()

	#load_to_database(categories)
	driver.get("https://products.wholefoodsmarket.com/product/santa-barbara-pistachio-santa-barbara-pistachio-organic-chile-lemon-pistachios-098f33")
	time.sleep(2)
	driver.find_elements_by_css_selector(".Collapsible-Root--3cwwH+ .Collapsible-Root--3cwwH .Collapsible-Title--30gLK")[0].click()
	p_name = driver.find_elements_by_css_selector(".ProductHeader-Name--1ysBV")[0].text
	serving_size = driver.find_elements_by_css_selector(".Separator__3rdE_+ .NutritionTable-Unbreakable--1UPcX")[0].text
	values = driver.find_elements_by_css_selector(".NutritionTable-Root--YcoZx")[0].text
	values = str.join(" ", values.splitlines())

	tot_fat = re.findall(r"(?<=Total Fat )[\d\|.]+", values)[0]
	tot_cholesterol = re.findall(r"(?<=Cholesterol )[\d\|.]+", values)[0]
	tot_protein = re.findall(r"(?<=Protein )[\d\|.]+", values)[0]
	tot_carbs = re.findall(r"(?<=Total Carbohydrates )[\d\|.]+", values)[0]
	tot_calories = re.findall(r"(?<=Calories )[\d\|.]+", values)[0]

	print("Name{}".format(p_name))
	print("Serving Size {}".format(serving_size))
	print("Cholesterol {}".format(tot_cholesterol))
	print("Protein {}".format(tot_protein))
	print("Calories {}".format(tot_calories))
	print("Carbs {}".format(tot_carbs))
	print("Fat {}".format(tot_fat))

	img = driver.find_elements_by_css_selector(".ImagePreviewer-Thumbnail--lEL4J:nth-child(1)")[0].get_attribute('style')
	img = img.split('url("')[1].split("\");")[0]

	blobData = get_blob(img)
	print(blobData)

	driver.get(img)
	time.sleep(2)
	# End the driver session
	driver.quit()

