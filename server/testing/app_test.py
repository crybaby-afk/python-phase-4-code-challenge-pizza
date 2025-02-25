import pytest
from models import Restaurant, RestaurantPizza, Pizza
from app import app, db
from faker import Faker

class TestApp:
    '''Flask application in app.py'''

    def setup_method(self):
        """Runs before each test to reset the database."""
        with app.app_context():
            db.session.rollback()
            db.drop_all()
            db.create_all()

    def test_restaurants(self):
        """Retrieves restaurants with GET request to /restaurants"""
        with app.app_context():
            fake = Faker()
            restaurant1 = Restaurant(name=fake.name(), address=fake.address())
            restaurant2 = Restaurant(name=fake.name(), address=fake.address())
            db.session.add_all([restaurant1, restaurant2])
            db.session.commit()

            response = app.test_client().get('/restaurants')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            response_data = response.json
            assert len(response_data) == 2  
            for restaurant in response_data:
                assert 'restaurant_pizzas' not in restaurant  

    def test_restaurants_id(self):
        '''Retrieves one restaurant using its ID with GET request to /restaurants/<int:id>.'''
        with app.app_context():
            fake = Faker()
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().get(f'/restaurants/{restaurant.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            response_data = response.json
            assert response_data['id'] == restaurant.id
            assert response_data['name'] == restaurant.name
            assert response_data['address'] == restaurant.address
            assert 'restaurant_pizzas' in response_data  

    def test_returns_404_if_no_restaurant_to_get(self):
        '''Returns 404 for a non-existent restaurant ID.'''
        with app.app_context():
            response = app.test_client().get('/restaurants/0')
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error') == "Restaurant not found"

    def test_deletes_restaurant_by_id(self):
        '''Deletes restaurant with DELETE request to /restaurants/<int:id>.'''
        with app.app_context():
            fake = Faker()
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().delete(f'/restaurants/{restaurant.id}')
            assert response.status_code == 204  

            result = Restaurant.query.filter_by(id=restaurant.id).one_or_none()
            assert result is None  

    def test_returns_404_if_no_restaurant_to_delete(self):
        '''Returns 404 for a non-existent restaurant delete attempt.'''
        with app.app_context():
            response = app.test_client().delete('/restaurants/0')  
            assert response.status_code == 404
            assert response.json.get('error') == "Restaurant not found"

    def test_pizzas(self):
        """Retrieves pizzas with GET request to /pizzas"""
        with app.app_context():
            fake = Faker()
            pizza1 = Pizza(name=fake.name(), ingredients=fake.sentence())
            pizza2 = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add_all([pizza1, pizza2])
            db.session.commit()

            response = app.test_client().get('/pizzas')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            response_data = response.json
            assert len(response_data) == 2  
            for pizza in response_data:
                assert 'restaurant_pizzas' not in pizza  

    def test_creates_restaurant_pizzas(self):
        '''Creates a restaurant_pizza using a POST request to /restaurant_pizzas.'''
        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add_all([pizza, restaurant])
            db.session.commit()

            response = app.test_client().post(
                '/restaurant_pizzas',
                json={"price": 3, "pizza_id": pizza.id, "restaurant_id": restaurant.id}
            )

            assert response.status_code == 201
            assert response.content_type == 'application/json'

            response_data = response.json
            assert response_data['price'] == 3
            assert response_data['pizza_id'] == pizza.id
            assert response_data['restaurant_id'] == restaurant.id

            query_result = RestaurantPizza.query.filter_by(
                restaurant_id=restaurant.id, pizza_id=pizza.id
            ).first()
            assert query_result.price == 3  

    def test_400_for_validation_error(self):
        '''Returns a 400 status code and error message if a POST request fails due to validation errors.'''
        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add_all([pizza, restaurant])
            db.session.commit()

            for invalid_price in [0, 31]:  
                response = app.test_client().post(
                    '/restaurant_pizzas',
                    json={"price": invalid_price, "pizza_id": pizza.id, "restaurant_id": restaurant.id}
                )

                assert response.status_code == 400
                assert "errors" in response.json
                assert isinstance(response.json['errors'], list)
                assert len(response.json['errors']) > 0

                db.session.rollback()  
