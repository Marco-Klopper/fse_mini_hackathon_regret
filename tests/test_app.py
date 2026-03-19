"""
Integration tests for Flask routes.
"""
import pytest
import json
import os
import tempfile
from app import app, db, load_categories, get_home_price
from models import UserInput


@pytest.fixture
def client():
    """Create test client with temporary database."""
    # Create temp database
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
    
    client = app.test_client()

    # Patch commodity data to avoid external API calls
    app.fetch_commodity_data = lambda: [
        {'date': '2025-01-01', 'price': 100},
        {'date': '2025-02-01', 'price': 105},
        {'date': '2025-03-01', 'price': 110},
    ]

    yield client
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


class TestHomeRoute:
    """Test home route."""
    
    def test_home_route_returns_200(self, client):
        """Test that home route returns 200 status."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_route_returns_html(self, client):
        """Test that home route returns HTML template."""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'


class TestLoadCategories:
    """Test category loading."""
    
    def test_load_categories_returns_list(self):
        """Test that load_categories returns a list."""
        categories = load_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
    
    def test_load_categories_has_required_fields(self):
        """Test that categories have name and home_price."""
        categories = load_categories()
        for category in categories:
            assert 'name' in category
            assert 'home_price' in category
            assert isinstance(category['home_price'], float)
    
    def test_load_categories_contains_expected_items(self):
        """Test that expected categories are loaded."""
        categories = load_categories()
        category_names = [c['name'] for c in categories]
        assert 'Burgers' in category_names
        assert 'Pizza' in category_names
        assert 'Coffee' in category_names


class TestGetHomePrice:
    """Test home price retrieval."""
    
    def test_get_home_price_returns_float(self):
        """Test that get_home_price returns a float."""
        price = get_home_price('Burgers')
        assert isinstance(price, float)
        assert price > 0
    
    def test_get_home_price_case_insensitive(self):
        """Test that category lookup is case insensitive."""
        price1 = get_home_price('Burgers')
        price2 = get_home_price('burgers')
        assert price1 == price2
    
    def test_get_home_price_raises_on_invalid_category(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError):
            get_home_price('InvalidCategory')


class TestResultRoute:
    """Test result calculation route."""
    
    def test_result_route_requires_post(self, client):
        """Test that result route requires POST."""
        response = client.get('/result')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_result_route_with_valid_input(self, client):
        """Test result route with valid input."""
        # Mock commodity data to avoid external API calls
        app.fetch_commodity_data = lambda: [
            {'date': '2025-01-01', 'price': 100},
            {'date': '2025-02-01', 'price': 105},
            {'date': '2025-03-01', 'price': 110},
        ]

        payload = {
            'price': 200,
            'category': 'Burgers',
            'delivery_option': 'pickup'
        }
        response = client.post(
            '/result',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'regret_score' in data
        assert 'difference_saved' in data
    
    def test_result_route_calculates_delivery_fee(self, client):
        """Test that delivery fee is calculated."""
        # Delivery option
        payload_delivery = {
            'price': 200,
            'category': 'Burgers',
            'delivery_option': 'delivery'
        }
        response = client.post(
            '/result',
            data=json.dumps(payload_delivery),
            content_type='application/json'
        )
        data_delivery = json.loads(response.data)
        
        # Pickup option
        payload_pickup = {
            'price': 200,
            'category': 'Burgers',
            'delivery_option': 'pickup'
        }
        response = client.post(
            '/result',
            data=json.dumps(payload_pickup),
            content_type='application/json'
        )
        data_pickup = json.loads(response.data)
        
        # Delivery should have higher fee
        assert data_delivery['delivery_fee'] == 50
        assert data_pickup['delivery_fee'] == 0
    
    def test_result_route_missing_fields(self, client):
        """Test result route with missing fields."""
        payload = {'price': 200}  # Missing category and delivery_option
        response = client.post(
            '/result',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_result_route_invalid_price(self, client):
        """Test result route with invalid price."""
        payload = {
            'price': 'invalid',
            'category': 'Burgers',
            'delivery_option': 'pickup'
        }
        response = client.post(
            '/result',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_result_route_stores_data(self, client):
        """Test that result route stores data in database."""
        with app.app_context():
            initial_count = UserInput.query.count()
            
            payload = {
                'price': 200,
                'category': 'Burgers',
                'delivery_option': 'pickup'
            }
            response = client.post(
                '/result',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            final_count = UserInput.query.count()
            assert final_count == initial_count + 1
            
            # Check stored data
            latest = UserInput.query.order_by(UserInput.id.desc()).first()
            assert latest.price == 200
            assert latest.category == 'Burgers'
            assert latest.delivery_option == 'pickup'


class TestDataPersistence:
    """Test data persistence."""
    
    def test_user_input_model_to_dict(self, client):
        """Test UserInput model to_dict method."""
        payload = {
            'price': 150,
            'category': 'Pizza',
            'delivery_option': 'delivery'
        }
        response = client.post(
            '/result',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            user_input = UserInput.query.order_by(UserInput.id.desc()).first()
            user_dict = user_input.to_dict()
            
            assert user_dict['price'] == 150
            assert user_dict['category'] == 'Pizza'
            assert 'created_at' in user_dict
            assert 'regret_score' in user_dict
