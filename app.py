"""
Regret Meter Flask Application
Main entry point for the takeout vs cooking at home regret meter.
"""
from flask import Flask, render_template, request, jsonify
from models import db, UserInput, CommodityData
from api_handler import fetch_commodity_data
from calculations import (
    calculate_regret_score,
    simulate_investment,
    calculate_commodity_growth,
)
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR}/regret_meter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def home():
    """Home page - input form for takeout meal."""
    try:
        # Load categories from CSV
        categories = load_categories()
        return render_template('home.html', categories=categories)
    except Exception as e:
        return jsonify({'error': f'Error loading categories: {str(e)}'}), 500


@app.route('/result', methods=['POST'])
def result():
    """
    Result page - display regret score and commodity price graph.
    Expected JSON payload:
    {
        "price": float,
        "category": str,
        "delivery_option": str (delivery/pickup)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['price', 'category', 'delivery_option']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        takeout_price = float(data['price'])
        category = data['category']
        delivery_option = data['delivery_option']
        
        # Fetch commodity data (last 12 months)
        commodity_data = fetch_commodity_data()
        
        # Load home price for category
        home_price = get_home_price(category)
        
        # Calculate delivery fee
        delivery_fee = 50 if delivery_option.lower() == 'delivery' else 0
        
        # Calculate difference saved
        difference_saved = takeout_price - home_price - delivery_fee
        
        # Calculate investment returns using gold only
        investment_data = simulate_investment(difference_saved, commodity_data)
        commodity_growth = calculate_commodity_growth(investment_data) if investment_data else 0

        # Calculate regret score
        regret_score = calculate_regret_score(
            difference_saved=difference_saved,
            takeout_price=takeout_price,
            commodity_growth=commodity_growth
        )

        # Store user input in database
        user_input = UserInput(
            price=takeout_price,
            category=category,
            delivery_option=delivery_option,
            home_price=home_price,
            delivery_fee=delivery_fee,
            difference_saved=difference_saved,
            commodity_growth=commodity_growth,
            regret_score=regret_score,
            created_at=datetime.utcnow()
        )
        db.session.add(user_input)
        db.session.commit()

        # Graph data uses only gold prices and investment returns
        graph_data = investment_data

        return jsonify({
            'regret_score': regret_score,
            'difference_saved': difference_saved,
            'commodity_growth': commodity_growth,
            'graph_data': graph_data,
            'category': category,
            'takeout_price': takeout_price,
            'home_price': home_price,
            'delivery_fee': delivery_fee
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error calculating regret score: {str(e)}'}), 500


def load_categories():
    """Load food categories from CSV file."""
    categories = []
    csv_path = os.path.join(BASE_DIR, 'categories.csv')
    
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, 'r') as f:
        lines = f.readlines()[1:]  # Skip header
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                categories.append({
                    'name': parts[0].strip(),
                    'home_price': float(parts[1].strip())
                })
    
    return categories


def get_home_price(category):
    """Get home-cooked price for a category."""
    categories = load_categories()
    for cat in categories:
        if cat['name'].lower() == category.lower():
            return cat['home_price']
    raise ValueError(f'Category {category} not found')




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
