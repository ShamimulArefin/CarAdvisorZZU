import pytest
from flask import Flask
from CarAdvisor.app.routes import create_app
from CarAdvisor.utils.carRecommendation import recommended_cars
from CarAdvisor.utils.pricePrediction import price_prediction

@pytest.fixture
def app():
    app = create_app()
    # app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to CarAdvisor' in response.data

def test_user_registration(client):
    response = client.post('/register', data=dict(
        fullname='Test User',
        email='test@example.com',
        username='testuser',
        password='password123'
    ), follow_redirects=True)
    assert b'Account Created Successfully!' in response.data

def test_user_login(client):
    response = client.post('/login', data=dict(
        username='testuser',
        password='password123'
    ), follow_redirects=True)
    assert b'Welcome back, Test User' in response.data

def test_car_recommendation():
    features = ["American", "light color", "luxury_small", (5000, 10000), "automatic"]
    cars, col_names = recommended_cars(tuple(features))
    assert cars is not None
    assert col_names is not None

def test_price_prediction():
    features = [2003, 207000.0, 6, 'harley-davidson', 'davidson', 'gas', 'clean', 'automatic', 'excellent', 'rwd', 'pickup']
    predicted_price = price_prediction(features)
    assert isinstance(predicted_price, float)
