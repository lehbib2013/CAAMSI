import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_products(client):
    response = client.get('/api/products/')
    assert response.status_code == 200
    assert response.json == []

def test_add_product(client):
    response = client.post('/api/products/', json={
        "name": "Test Product",
        "price": 10.99,
        "stock": 100
    })
    assert response.status_code == 201
    assert response.json['message'] == "Produit ajouté avec succès!"