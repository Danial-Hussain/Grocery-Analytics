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

# Gets the latest version of chrome driver and caches it
driver = webdriver.Chrome(ChromeDriverManager().install())
BASEURL = "https://products.wholefoodsmarket.com/search?sort=relevance"
# Store category names with their links
categories = {}

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
	with open('products.json', 'w') as fp:
		json.dump(categories, fp, indent = 4)



	


if __name__ == "__main__":
	driver.quit()

	