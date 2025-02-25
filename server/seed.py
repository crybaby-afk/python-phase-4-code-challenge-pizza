#!/usr/bin/env python3

from server.app import app
from models import db, Restaurant, Pizza, RestaurantPizza

with app.app_context():
    print("Deleting data...")
    db.session.query(RestaurantPizza).delete()
    db.session.query(Pizza).delete()
    db.session.query(Restaurant).delete()

    print("Creating restaurants...")
    shack = Restaurant(name="Karen's Pizza Shack", address="123 Main St")
    bistro = Restaurant(name="Sanjay's Pizza", address="456 Side St")
    palace = Restaurant(name="Kiki's Pizza", address="789 Park Ave")
    restaurants = [shack, bistro, palace]

    print("Creating pizzas...")
    cheese = Pizza(name="Margherita", ingredients="Dough, Tomato Sauce, Cheese")
    pepperoni = Pizza(name="Pepperoni", ingredients="Dough, Tomato Sauce, Cheese, Pepperoni")
    california = Pizza(name="California Style", ingredients="Dough, Sauce, Ricotta, Red Peppers, Mustard")
    pizzas = [cheese, pepperoni, california]

    print("Creating RestaurantPizza...")
    pr1 = RestaurantPizza(restaurant=shack, pizza=cheese, price=10)
    pr2 = RestaurantPizza(restaurant=bistro, pizza=pepperoni, price=15)
    pr3 = RestaurantPizza(restaurant=palace, pizza=california, price=20)

    db.session.add_all(restaurants)
    db.session.add_all(pizzas)
    db.session.add_all([pr1, pr2, pr3])
    db.session.commit()

    print("Seeding done!")
