#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os

from models import db, Restaurant, RestaurantPizza, Pizza

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
    return "<h1>Code Challenge API</h1>"

class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas], 200

api.add_resource(PizzaResource, "/pizzas")

class RestaurantResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants], 200  # ✅ FIXED

api.add_resource(RestaurantResource, "/restaurants")

class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(rules=("-restaurant_pizzas.restaurant",)), 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        RestaurantPizza.query.filter_by(restaurant_id=id).delete(synchronize_session=False)

        db.session.delete(restaurant)
        db.session.commit()
        return "", 204

api.add_resource(RestaurantByIdResource, "/restaurants/<int:id>")

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()

        required_fields = ["price", "pizza_id", "restaurant_id"]
        if not all(field in data for field in required_fields):
            return {"errors": ["Missing required fields"]}, 400

        try:
            price = int(data["price"])
            if not (1 <= price <= 30):
                return {"errors": ["Price must be between 1 and 30"]}, 400

            pizza = db.session.get(Pizza, data["pizza_id"])
            restaurant = db.session.get(Restaurant, data["restaurant_id"])
            if not pizza or not restaurant:
                return {"errors": ["Invalid pizza_id or restaurant_id"]}, 400

            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return new_restaurant_pizza.to_dict(rules=("-restaurant", "-pizza")), 201

        except ValueError:
            return {"errors": ["Price must be an integer"]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 400

api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
