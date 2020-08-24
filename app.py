from flask import Flask, render_template, request, jsonify, json, flash, redirect, url_for
from wtforms import StringField, TextField, Form
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from methods_for_dashboard import getTotals, createBarChart
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///data/product_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '9240bf46152dfe0b193531626c625c00'
app.config['DEBUG'] = True

db = SQLAlchemy(app) 

Base = declarative_base()

class Product(db.Model):
	__tablename__ = "product"
	product_id = Column('id', Integer, primary_key = True, index = True, autoincrement = True)
	category = Column('category', String(500))
	subcategory = Column('subcategory', String(500))
	name = Column('name', String(500))
	serving = Column('serving', String(500), nullable = True)
	calories = Column('calories', Numeric, nullable = True)
	fat = Column('fat', Numeric, nullable = True)
	carbohydrates = Column('carbohydrates', Numeric, nullable = True)
	protein = Column('protein', Numeric, nullable = True)
	cholesterol = Column('cholesterol', Numeric, nullable = True)
	url = Column('url', String(500), nullable = True)
	def as_dict(self):
		return {'name': self.name}


class SearchForm(Form): #create form
	name = StringField('Name', validators=[DataRequired(),Length(min= 5, max=40)],render_kw={"placeholder": "Enter a product"})


# Hold the user's cart
userCart = []


@app.route('/')
def home():
	"""
	Home Page
	"""
	form = SearchForm(request.form)
	return render_template('index.html' , form=form)

@app.route('/products')
def productdic():
	"""
	Used for live search
	"""
	res = Product.query.all()
	names = [r.as_dict() for r in res]
	return jsonify(names)

@app.route('/process', methods=['POST'])
def process():
	"""
	Gets data for product from the sql database
	"""
	try:
		product_name = request.form['name']
		query = db.session.query(Product).filter_by(name = product_name).one()
		product = {'name': query.name,
							 'serving': query.serving,
							 'calories': str(query.calories),
							 'fat': str(query.fat),
							 'carbohydrates': str(query.carbohydrates),
							 'protein': str(query.protein),
							 'cholesterol': str(query.cholesterol)}
		return product
	except:
		return jsonify({'name': "ERROR"})

@app.route('/cart')
def cart():
	"""
	Your shopping cart page
	"""
	tot_cal, tot_fat, tot_carb, tot_prot, tot_chol = getTotals(userCart)
	createBarChart(userCart)

	images = []

	for file in os.listdir("static"):
		if file.endswith(".png"):
			img = "../static" + "/" + file
			images.append(img)

	return render_template('cart.html', bars = images, cart = userCart, tot_cal = tot_cal, tot_fat = tot_fat, tot_carb = tot_carb, tot_prot = tot_prot, tot_chol = tot_chol)

@app.route('/visualizations')
def viz():
	"""
	Page for some interesting visualizations
	"""
	return render_template('data_viz.html')

@app.route('/submit', methods=['POST'])
def submit():
	"""
	Method that gets submitted data to be added to the cart
	"""
	product = request.form['pname']
	try:
		query = db.session.query(Product).filter_by(name = product).one()
		message = {'message': 'success'}
		userCart.append(product)
		return message
	except:
		message = {'message': 'failure'}
		return message


if __name__ == "__main__":
	app.run(debug = True) 