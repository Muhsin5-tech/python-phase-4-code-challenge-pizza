#!/usr/bin/env python3

from app import app
from models import db, Restaurant, Pizza, RestaurantPizza

with app.app_context():

    # This will delete any existing rows
    # so you can run the seed file multiple times without having duplicate entries in your database
    print("Deleting data...")
    Pizza.query.delete()
    Restaurant.query.delete()
    RestaurantPizza.query.delete()

    print("Creating restaurants...")
    r1 = Restaurant(name="Pizza Hut", address="123 Main St")
    r2 = Restaurant(name="Domino's", address="456 Elm St")
    r3 = Restaurant(name="Papa John's", address="789 Oak St")

    print("Creating pizzas...")
    p1 = Pizza(name="Cheese", ingredients="Cheese, Tomato Sauce, Dough")
    p2 = Pizza(name="Pepperoni", ingredients="Pepperoni, Cheese, Tomato Sauce, Dough")
    p3 = Pizza(name="Veggie", ingredients="Mushrooms, Peppers, Onions, Cheese, Dough")

    print("Creating restaurant-pizzas...")
    rp1 = RestaurantPizza(price=15, restaurant=r1, pizza=p1)
    rp2 = RestaurantPizza(price=20, restaurant=r2, pizza=p2)
    rp3 = RestaurantPizza(price=12, restaurant=r3, pizza=p3)

    db.session.add_all([r1, r2, r3, p1, p2, p3, rp1, rp2, rp3])
    db.session.commit()
    print("Seeding done!")
