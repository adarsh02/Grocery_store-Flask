from website.__init__ import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from  datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(10))
    cart_items=db.Relationship('Cart',backref='user')
    purchase_items=db.Relationship('User_History',backref='user')



class Cart(db.Model):
    cart_id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer,db.ForeignKey('items.item_id'))
    no_of_item=db.Column(db.Integer)

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True,autoincrement=True,nullable=False)
    category= db.Column(db.String(150))
    item_name = db.Column(db.String(150),unique=True)
    price = db.Column(db.Float)
    no_of_items_left=db.Column(db.Integer)
    expiry_date=db.Column(db.Date)
    manufacture_date=db.Column(db.Date)
    cart_items=db.Relationship('Cart',backref='items')
    purchase_items = db.relationship('User_History', backref='item')
    


class User_History(db.Model):
    purchase_id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    no_of_items=db.Column(db.Integer)
    date_of_purchase=db.Column(db.DateTime)
    address=db.Column(db.String(500))
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))

