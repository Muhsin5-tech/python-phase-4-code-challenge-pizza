#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Pizza Restaurant API</h1>"


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route('/restaurants', methods=['POST'])
def create_restaurant():
    data = request.get_json()

    name = data.get("name")
    address = data.get("address")

    if not name or not address:
        return make_response(
            jsonify({"errors": ["Validation error: Name and Address are required"]}),
            400,
        )

    new_restaurant = Restaurant(name=name, address=address)

    try:
        db.session.add(new_restaurant)
        db.session.commit()
        return make_response(jsonify(new_restaurant.to_dict()), 201)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"errors": [str(e)]}), 500)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    restaurant_data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id,
                "pizza_id": rp.pizza_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients,
                }
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }
    
    return make_response(jsonify(restaurant_data), 200)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    return make_response(jsonify({"error": "Restaurant not found"}), 404)


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['GET'])
def get_restaurant_pizzas():
    restaurant_pizzas = RestaurantPizza.query.all()
    response_data = []

    for rp in restaurant_pizzas:
        pizza = Pizza.query.get(rp.pizza_id)
        restaurant = Restaurant.query.get(rp.restaurant_id)

        response_data.append({
            "id": rp.id,
            "price": rp.price,
            "pizza_id": rp.pizza_id,
            "restaurant_id": rp.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            }
        })

    return jsonify(response_data)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")
    
    if not (1 <= price <= 30):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return make_response(jsonify({"errors": ["Invalid pizza or restaurant"]}), 400)
        
    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    
    db.session.add(restaurant_pizza)
    db.session.commit()
    
    response_data = {
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients,
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
        }
    }

    return make_response(jsonify(response_data), 201)

@app.route('/restaurant_pizzas/<int:id>', methods=['DELETE'])
def delete_restaurant_pizza(id):
    restaurant_pizza = RestaurantPizza.query.get(id)
    if restaurant_pizza:
        db.session.delete(restaurant_pizza)
        db.session.commit()
        return make_response('', 204)
    return make_response(jsonify({"error": "RestaurantPizza not found"}), 404) 


if __name__ == "__main__":
    app.run(port=5555, debug=True)
