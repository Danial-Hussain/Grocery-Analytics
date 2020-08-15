from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
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
	image = Column('image', LargeBinary, nullable = True)
	url = Column('url', String(500), nullable = True)
