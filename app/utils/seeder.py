from sqlalchemy.sql import text
import sqlalchemy as sqla
from faker import Faker
import random
import itertools
from PyQt5 import QtCore
from .resources_rc import *
		
fake = Faker()

def create_meatplant(cities,prop_types):
	return {
		'name':f"Мясокомбинат {random.randint(1,1000000)}",
		'city_id':random.choice(cities),
		'property_type_id':random.choice(prop_types),
		'year':int(fake.year()),
		'phone':fake.phone_number()
	}
	
def create_product_for_plant(plants,products):
	return {
		'meatplant_id':random.choice(plants),
		'product_id':random.choice(products),
		'volume':random.randint(10000,1000000),
		'price_per_kg':random.randint(100,5000)
	}
	
def create_order(clients,products,ordc,con):
	pi = random.choice(products)
	pv = con.execute(f'select volume from products_of_plants where id={pi}').scalar()
	return {
		'date':str(fake.date_between(start_date='-1y')),
		'product_id':pi,
		'volume':random.randint(1000,int(pv/ordc)),
		'client_id':random.choice(clients)
	}
	
def create_client(cities):
	return {
		'name':fake.company(),
		'phone':fake.phone_number(),
		'address':fake.address(),
		'city_id':random.choice(cities),
		'login':fake.user_name()
	}
	
def generate_meatplants(num, con):
	cities = [x[0] for x in con.execute('select id from cities')]
	prop_types = [x[0] for x in con.execute('select id from property_types')]
	products = [x[0] for x in con.execute('select id from products')]
	clients = [x[0] for x in con.execute('select id from clients')]
	if not (cities and prop_types and products and clients):
		return
	for n in range(num):
		mi = con.execute(text("insert into meatplants values(default, :name, :city_id, :phone, :year, :property_type_id) returning id"),create_meatplant(cities,prop_types)).scalar()
		while True:
			try:
				un = fake.user_name()
				with con.begin():
					con.execute(text(f"set role admin; create user {un} with encrypted password '0' in role manager;"),{})
					con.execute(text("insert into meatplants_managers values(default,:plant,:name)"),{'name':un,'plant':mi})
				break
			except sqla.exc.SQLAlchemyError as e:
				print(e)
		for i in range(10):
			try:
				pi = con.execute(text("insert into products_of_plants values(default, :meatplant_id, :product_id, :volume, :price_per_kg) returning id"),create_product_for_plant([mi],products)).scalar()
				for i in range(100):
					try:
						con.execute(text('insert into orders values(default, :date, :volume, :client_id, :product_id) returning id'),create_order(clients,[pi],10,con))
					except sqla.exc.SQLAlchemyError as e:
						print(e)
			except sqla.exc.SQLAlchemyError as e:
				print(e)

			
def generate_clients(num,con):
	cities = [x[0] for x in con.execute('select id from cities')]
	if not cities:
		return
	n = 0
	while n < num:
		try:
			cl = create_client(cities)
			with con.begin():
				con.execute(text(f"set role admin; create user {cl['login']} with encrypted password '0' in role client"),{})
				con.execute(text('insert into clients values(default, :name, :phone, :address, :city_id, :login) returning id'),cl)
			n += 1
		except sqla.exc.SQLAlchemyError as e:
			print(e)
		
def generate_cities(num,con):
	for i in range(num):
		try:
			con.execute(text('insert into cities values(default, :name)'),{'name':fake.city()})
		except:
			pass

def add_values(table,con):
	fie=QtCore.QFile(":/"+table+".txt")
	fie.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
	st = QtCore.QTextStream(fie)
	while not st.atEnd():
		i = st.readLine()
		try:
			con.execute(text(f'insert into {table} values(default, :v)'),{'v':i.lstrip("\ufeff").rstrip()})
		except Exception as e:
			print(e)
			pass
		
		
def add_base(con):
	add_values('property_types',con)
	add_values('product_names',con)
	add_values('product_types',con)
	names = [x[0] for x in con.execute('select id from product_names')]
	types = [x[0] for x in con.execute('select id from product_types')]
	for i in itertools.product(types, names):
		try:
			con.execute(text(f'insert into products values(default, :type_id, :name_id)'),{'type_id':i[0],'name_id':i[1]})
		except:
			pass

def standart_generate(con):
	try:
		add_base(con)
		generate_cities(10,con)
		generate_clients(10,con)
		generate_meatplants(10,con)
	except Exception as e:
		print(e)

