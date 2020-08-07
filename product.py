
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
	__tablename__ = "product"
	product_id = Column('id', String, primary_key = True, index = True)
	category = Column('category', String)
	subcategory = Column('subcategory', String)
	name = Column('name', String, unique = True)
	serving = Column('name', String)
	calories = Column('calories', Numeric)
	fat = Column('fat', Numeric)
	carbohydrates = Column('carbohydrates', Numeric)
	protein = Column('protein', Numeric)
	cholesterol = Column('cholesterol', Numeric)
