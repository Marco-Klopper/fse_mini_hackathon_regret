"""
Alpha Vantage API handler for fetching commodity price data.
"""
import requests
from models import db, CommodityData
from datetime import datetime, timedelta
import os

# Alpha Vantage API configuration
# Prefer environment variable to avoid committing secrets in source.
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'

# S&P 500 ETF (SPY) is used for investment growth calculations
CACHE_DURATION_HOURS = 24  # Cache data for 24 hours


def fetch_commodity_data():
    """Fetch last 12 months of S&P 500 price data from Alpha Vantage or database cache.

    Returns:
        list: List of dicts with date and price for last 12 months
    """
    try:
        cached_data = get_cached_data()
        if cached_data:
            return cached_data

        spy_data = fetch_symbol_data('SPY')
        if not spy_data:
            # Fall back to cached data if API call fails
            cached = get_cached_data(ignore_age=True)
            return cached if cached else _sample_spy_history()

        return build_spy_price_history(spy_data)

    except Exception as e:
        print(f'Error fetching commodity data: {str(e)}')
        cached = get_cached_data(ignore_age=True)
        return cached if cached else _sample_spy_history()


def _sample_spy_history():
    """Generate a fallback 12-month S&P 500 (SPY) price history (for offline/dev use)."""
    from datetime import datetime

    # Generate 12 months of synthetic prices.
    now = datetime.utcnow()
    data = []
    base_price = 450.0
    for i in range(12, 0, -1):
        dt = now.replace(day=1)
        month = dt.month - i
        year = dt.year
        while month <= 0:
            month += 12
            year -= 1
        date_str = f"{year:04d}-{month:02d}-01"
        # Synthetic trend + volatility
        price = base_price + (i * 2.5) + ((i % 3) * 3.0)
        data.append({
            'date': date_str,
            'price': round(price, 2)
        })
    return data


def fetch_symbol_data(symbol):
    """Fetch monthly price data for a commodity symbol from Alpha Vantage."""
    params = {
        'function': 'TIME_SERIES_MONTHLY',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'Error Message' in data:
            print(f'API Error: {data["Error Message"]}')
            return None

        if 'Note' in data:
            print(f'API Rate Limit: {data["Note"]}')
            return None

        time_series_key = 'Time Series (Monthly)'
        if time_series_key not in data:
            print(f'Unexpected API response format for {symbol}')
            return None

        time_series = data[time_series_key]

        # Cache the data in database
        for date_str, price_data in time_series.items():
            cache_price_data(symbol, date_str, price_data)

        return time_series

    except requests.exceptions.RequestException as e:
        print(f'Request error fetching {symbol}: {str(e)}')
        return None
    except Exception as e:
        print(f'Error processing {symbol} data: {str(e)}')
        return None


def cache_price_data(symbol, date_str, price_data):
    """Cache price data in the database."""
    try:
        existing = CommodityData.query.filter_by(symbol=symbol, date=date_str).first()

        if not existing:
            commodity = CommodityData(
                symbol=symbol,
                date=date_str,
                open_price=float(price_data.get('1. open', 0)),
                close_price=float(price_data.get('4. close', 0)),
                high_price=float(price_data.get('2. high', 0)),
                low_price=float(price_data.get('3. low', 0)),
                volume=float(price_data.get('5. volume', 0)) if '5. volume' in price_data else None,
                fetched_at=datetime.utcnow()
            )
            db.session.add(commodity)
        else:
            existing.fetched_at = datetime.utcnow()

        db.session.commit()
    except Exception as e:
        print(f'Error caching data: {str(e)}')
        db.session.rollback()


def get_cached_data(ignore_age=False):
    """Get cached S&P 500 (SPY) data from database."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(hours=CACHE_DURATION_HOURS)

        if ignore_age:
            spy_data = CommodityData.query.filter_by(symbol='SPY').all()
        else:
            spy_data = CommodityData.query.filter_by(symbol='SPY').filter(
                CommodityData.fetched_at >= cutoff_date
            ).all()

        if not spy_data:
            return None

        return spy_data

    except Exception as e:
        print(f'Error retrieving cached data: {str(e)}')
        return None


def build_spy_price_history(spy_data):
    """Build a chronological list of S&P 500 prices for the last 12 months."""
    common_dates = sorted(spy_data.keys(), reverse=True)[:12]
    common_dates = sorted(common_dates)

    return [
        {'date': date, 'price': float(spy_data[date].get('4. close', 0))}
        for date in common_dates
    ]


def clear_old_cache(days=30):
    """Clear cached data older than specified days."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        CommodityData.query.filter(CommodityData.fetched_at < cutoff_date).delete()
        db.session.commit()
        print(f'Cleared cache data older than {days} days')
    except Exception as e:
        print(f'Error clearing cache: {str(e)}')
        db.session.rollback()
