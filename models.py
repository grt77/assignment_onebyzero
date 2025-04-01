from datetime import datetime
from collections import defaultdict

class Transactions:
    def __init__(self,transation_id,product_id,amount,datetime_str):
        self.transation_id=transation_id
        self.product_id=product_id
        self.amount=float(amount)
        self.datetime=datetime.strptime(datetime_str,"%Y-%m-%d %H:%M:%S")

class Product:
    def __init__(self,product_id,name,city):
        self.product_id=product_id
        self.name=name
        self.city=city

class DataStore:
    def __init__(self):
        self.transactions={}
        self.products={}
        


