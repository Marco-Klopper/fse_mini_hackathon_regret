from datetime import datetime
import os
import requests

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regret.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    delivery = db.Column(db.String(20), nullable=False)
    regret_score = db.Column(db.Float, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

# Home made baseline prices by category
HOME_PRICES = {
    'burgers': 45.0,
    'pizza': 35.0,
    'chinese': 40.0,
    'coffee': 20.0,
    'other': 30.0,
}

DELIVERY_FEE = 50.0

# static last 12 month data (mock values). Format: {month label, gold, silver}
DEFAULT_COMMODITY_SERIES = [
    {'month': '2024-04', 'gold': 200.5, 'silver': 22.4},
    {'month': '2024-05', 'gold': 203.0, 'silver': 23.1},
    {'month': '2024-06', 'gold': 198.7, 'silver': 22.8},
    {'month': '2024-07', 'gold': 204.4, 'silver': 23.6},
    {'month': '2024-08', 'gold': 211.1, 'silver': 24.3},
    {'month': '2024-09', 'gold': 209.9, 'silver': 24.0},
    {'month': '2024-10', 'gold': 212.7, 'silver': 25.0},
    {'month': '2024-11', 'gold': 215.3, 'silver': 25.7},
    {'month': '2024-12', 'gold': 219.8, 'silver': 26.5},
    {'month': '2025-01', 'gold': 222.0, 'silver': 26.0},
    {'month': '2025-02', 'gold': 224.6, 'silver': 26.9},
    {'month': '2025-03', 'gold': 228.1, 'silver': 27.2},
]


def get_commodity_series():
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    if not api_key:
        return DEFAULT_COMMODITY_SERIES

    def fetch(symbol):
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_MONTHLY',
            'symbol': symbol,
            'apikey': api_key,
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            timeseries = data.get('Monthly Time Series', {})
            if not timeseries:
                return None
            # sort descending date and take last 12 months oldest to newest.
            dates = sorted(timeseries.keys())[-12:]
            return [
                {
                    'month': d,
                    'gold': float(timeseries[d]['4. close']) if symbol == 'GLD' else None,
                    'silver': float(timeseries[d]['4. close']) if symbol == 'SLV' else None,
                }
                for d in dates
            ]
        except Exception:
            return None

    gld = fetch('GLD')
    slv = fetch('SLV')

    if not gld or not slv or len(gld) != len(slv):
        return DEFAULT_COMMODITY_SERIES

    merged = []
    for i in range(len(gld)):
        merged.append({'month': gld[i]['month'], 'gold': gld[i]['gold'], 'silver': slv[i]['silver']})

    return merged


def compute_regret(amount, category, delivery):
    home_cost = HOME_PRICES.get(category, HOME_PRICES['other'])
    fee = DELIVERY_FEE if delivery == 'delivery' else 0.0

    difference_saved = max(amount - home_cost - fee, 0.0)
    savings_ratio = 0.0
    if amount > 0:
        savings_ratio = (difference_saved / amount) * 100

    series = get_commodity_series()
    gold_start = series[0]['gold']
    gold_end = series[-1]['gold']
    silver_start = series[0]['silver']
    silver_end = series[-1]['silver']

    gold_growth = ((gold_end - gold_start) / gold_start * 100) if gold_start else 0.0
    silver_growth = ((silver_end - silver_start) / silver_start * 100) if silver_start else 0.0
    commodity_growth = (gold_growth + silver_growth) / 2.0

    # reg formula from plan
    raw_score = (savings_ratio) + (commodity_growth / 2.0)
    regret_score = min(100.0, max(0.0, raw_score))

    # Determine regret level
    if regret_score < 20:
        level = 'Low regret'
        color = 'var(--low)'
    elif regret_score < 50:
        level = 'Mild regret'
        color = 'var(--medium)'
    elif regret_score < 80:
        level = 'Risky decision'
        color = 'var(--high)'
    else:
        level = 'High regret'
        color = 'var(--critical)'

    # Simulate cumulative gains each month for difference_saved investment
    monthly_gains = []
    investment = difference_saved
    if investment <= 0:
        investment = 0

    cumulative_invested = 0
    for idx, point in enumerate(series, start=1):
        if idx == 1:
            cumulative_invested = investment
        else:
            previous = series[idx-2]
            monthly_gain_pct = ((point['gold'] / previous['gold'] - 1.0) +
                                 (point['silver'] / previous['silver'] - 1.0)) / 2.0
            cumulative_invested *= 1 + monthly_gain_pct
        monthly_gains.append({'month': point['month'], 'value': round(cumulative_invested, 2)})

    return {
        'amount': amount,
        'category': category,
        'delivery': delivery,
        'home_cost': home_cost,
        'fee': fee,
        'difference_saved': round(difference_saved, 2),
        'savings_ratio': round(savings_ratio, 2),
        'commodity_growth': round(commodity_growth, 2),
        'regret_score': round(regret_score, 2),
        'regret_level': level,
        'regret_color': color,
        'monthly_gains': monthly_gains,
        'commodity_series': series,
    }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    try:
        amount = float(request.form.get('amount', '0'))
    except ValueError:
        amount = None

    if amount is None or amount <= 0:
        flash('Please enter a valid positive amount for takeout price.')
        return redirect(url_for('home'))

    category = request.form.get('category', 'other')
    delivery = request.form.get('delivery', 'pickup')

    result_data = compute_regret(amount, category, delivery)

    # save to DB (optional)
    try:
        record = UserInput(
            amount=result_data['amount'],
            category=category,
            delivery=delivery,
            regret_score=result_data['regret_score'],
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return render_template('result.html', **result_data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
