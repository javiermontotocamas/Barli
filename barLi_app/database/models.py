from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from barLi_app.utils.db import db


class User(db.Model, UserMixin):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_fullname = db.Column(db.String(30), nullable=False)
    user_telephone = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String(30), nullable=False, unique=True)
    user_password = db.Column(db.Text, nullable=False)
    user_birth = db.Column(db.DateTime, nullable=False)
    user_district = db.Column(db.Integer, db.ForeignKey("Districts.district_id"), nullable=False)
    user_admin = db.Column(db.Boolean, nullable=False, default=False)
    book_user_id = db.relationship("Book", backref="user", lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_fullname, user_telephone, user_email, user_password, user_birth, user_admin, user_district):
        self.user_fullname = user_fullname
        self.user_telephone = user_telephone
        self.user_email = user_email
        self.user_password = generate_password_hash(user_password)
        self.user_birth = user_birth
        self.user_admin = user_admin
        self.user_district = user_district

    def check_pass(self, password):
        return check_password_hash(self.user_password, password)

    def check_admin(self):
        return self.user_admin


class Bar(db.Model, UserMixin):
    __tablename__ = "Bars"
    bar_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bar_fullname = db.Column(db.String(30), nullable=False)
    bar_address = db.Column(db.String(30), nullable=False)
    bar_email = db.Column(db.String(30), nullable=False)
    bar_password = db.Column(db.Text, nullable=False)
    bar_district = db.Column(db.Integer, db.ForeignKey("Districts.district_id"), nullable=False)
    book_bar_id = db.relationship("Book", backref="bar", lazy=True, cascade='all, delete-orphan')
    table_bar_id = db.relationship("Table", backref="bar", lazy=True, cascade='all, delete-orphan')

    def __init__(self, bar_fullname, bar_address, bar_email, bar_password, bar_district):
        self.bar_fullname = bar_fullname
        self.bar_address = bar_address
        self.bar_password = generate_password_hash(bar_password)
        self.bar_email = bar_email
        self.bar_district = bar_district

    def check_pass(self, password):
        return check_password_hash(self.bar_password, password)


class Advertiser(db.Model, UserMixin):
    __tablename__ = "Advertisers"
    add_fullname = db.Column(db.String(30), primary_key=True, nullable=False)
    add_quantity = db.Column(db.Integer, nullable=True)
    add_img = db.Column(db.String(30), nullable=False)
    add_email = db.Column(db.String(30), nullable=False)
    add_password = db.Column(db.Text, nullable=False)
    add_district = db.Column(db.Integer, db.ForeignKey("Districts.district_id"), nullable=False)

    def __init__(self, add_fullname, add_quantity, add_img, add_email, add_password, add_district):
        self.add_fullname = add_fullname
        self.add_quantity = add_quantity
        self.add_img = add_img
        self.add_password = generate_password_hash(add_password)
        self.add_email = add_email
        self.add_district = add_district

    def check_pass(self, password):
        return check_password_hash(self.add_password, password)


class Table(db.Model):
    __tablename__ = "Tables"
    table_id = db.Column(db.Integer, nullable=False, primary_key=True)
    table_seat_num = db.Column(db.Integer, nullable=False)
    table_bar = db.Column(db.Integer, db.ForeignKey("Bars.bar_id"), nullable=False)
    table_inside = db.Column(db.Boolean, nullable=False, default=True)
    # Si está en false, significa que está libre
    table_state = db.Column(db.Boolean, nullable=False, default=False)
    book_table_id = db.relationship("Books", backref="table", lazy=True, cascade='all, delete-orphan')

    def __init__(self, table_seat_num, table_bar, table_inside, table_state):
        self.table_seat_num = table_seat_num
        self.table_bar = table_bar
        self.table_inside = table_inside
        self.table_state = table_state


class Book(db.Model):
    __tablename__ = "Books"
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_user = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    book_table = db.Column(db.Integer, db.ForeignKey("Tables.table_id"), nullable=False, unique=True)
    book_bar = db.Column(db.Integer, db.ForeignKey("Bars.bar_id"), nullable=False)
    book_expiration = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(minutes=15))
    book_completed = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, book_user, book_table, book_bar, book_expiration, book_completed):
        self.book_user = book_user
        self.book_table = book_table
        self.book_bar = book_bar
        self.book_expiration = book_expiration
        self.book_completed = book_completed


class City(db.Model):
    __tablename__ = "Cities"
    city_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_fullname = db.Column(db.String(30), nullable=False)
    city_district_id = db.relationship("District", backref="city", lazy=True, cascade='all, delete-orphan')

    def __init__(self, city_fullname):
        self.city_fullname = city_fullname


class District(db.Model):
    __tablename__ = "Districts"
    district_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_fullname = db.Column(db.String(30), nullable=False)
    district_city = db.Column(db.Integer, db.ForeignKey("Cities.city_id"), nullable=False)

    def __init__(self, district_fullname, district_city):
        self.district_fullname = district_fullname
        self.district_city = district_city
