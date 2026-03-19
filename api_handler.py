"""
Alpha Vantage API handler for fetching commodity price data.
"""
import requests
from models import db, CommodityData
from datetime import datetime, timedelta
import os

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'

# Commodity symbols
# GLD: Gold ETF, SLV: Silver ETF
COMMODITY_SYMBOLS = ['GLD', 'SLV']
CACHE_DURATION_HOURS = 24  # Cache data for 24 hours


def fetch_commodity_data():
    """
    Fetch last 12 months of commodity data from Alpha Vantage or database cache.
    
    Returns:
        list: List of dicts with date, gold_price, and silver_price for last 12 months
    """
    try:
        # Check if we have recent cached data
        cached_data = get_cached_data()
        if cached_data:
            return cached_data
        
        # Fetch new data from API
        gold_data = fetch_symbol_data('GLD')
        silver_data = fetch_symbol_data('SLV')
        
        if not gold_data or not silver_data:
            # Fall back to cached data if API call fails
            return get_cached_data(ignore_age=True)
        
        # Merge gold and silver data
        merged_data = merge_commodity_data(gold_data, silver_data)
        
        return merged_data
    
    except Exception as e:
        print(f'Error fetching commodity data: {str(e)}')
        # Fall back to cached data
        return get_cached_data(ignore_age=True)


def fetch_symbol_data(symbol):
    """
    Fetch monthly price data for a commodity symbol from Alpha Vantage.
    
    Args:
        symbol (str): 'GLD' for gold or 'SLV' for silver
    
    Returns:
        dict: Price data keyed by date in YYYY-MM-DD format
    """
    params = {
        'function': 'TIME_SERIES_MONTHLY',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle API errors
        if 'Error Message' in data:
            print(f'API Error: {data["Error Message"]}')
            return None
        
        if 'Note' in data:
            print(f'API Rate Limit: {data["Note"]}')
            return None
        
        # Extract time series data
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
    """
    Cache price data in the database.
    
    Args:
        symbol (str): 'GLD' or 'SLV'
        date_str (str): Date in YYYY-MM-DD format
        price_data (dict): Price data with 'open', 'close', 'high', 'low', 'volume'
    """
    try:
        # Check if record already exists
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
            # Update fetched_at timestamp for existing records
            existing.fetched_at = datetime.utcnow()
        
        db.session.commit()
    
    except Exception as e:
        print(f'Error caching data: {str(e)}')
        db.session.rollback()


def get_cached_data(ignore_age=False):
    """
    Get cached commodity data from database.
    
    Args:
        ignore_age (bool): If True, return cached data regardless of age
    
    Returns:
        list: List of dicts with date, gold_price, silver_price for last 12 months
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(hours=CACHE_DURATION_HOURS)
        
        # Query recent data
        if ignore_age:
            gold_data = CommodityData.query.filter_by(symbol='GLD').all()
            silver_data = CommodityData.query.filter_by(symbol='SLV').all()
        else:
            gold_data = CommodityData.query.filter_by(symbol='GLD').filter(
                CommodityData.fetched_at >= cutoff_date
            ).all()
            silver_data = CommodityData.query.filter_by(symbol='SLV').filter(
                CommodityData.fetched_at >= cutoff_date
            ).all()
        
        if not gold_data or not silver_data:
            return None
        
        # Get last 12 months
        gold_dict = {d.date: d.close_price for d in gold_data}
        silver_dict = {d.date: d.close_price for d in silver_data}
        
        # Only keep dates that exist in both
        common_dates = set(gold_dict.keys()) & set(silver_dict.keys())
        
        if not common_dates:
            return None
        
        # Sort by date and get last 12
        sorted_dates = sorted(common_dates, reverse=True)[:12]
        sorted_dates = sorted(sorted_dates)  # Re-sort ascending for chronological order
        
        merged_data = [
            {
                'date': date,
                'gold_price': gold_dict[date],
                'silver_price': silver_dict[date]
            }
            for date in sorted_dates
        ]
        
        return merged_data if len(merged_data) >= 12 else None
    
    except Exception as e:
        print(f'Error retrieving cached data: {str(e)}')
        return None


def merge_commodity_data(gold_data, silver_data):
    """
    Merge gold and silver data into a single list.
    
    Args:
        gold_data (dict): Gold price data keyed by date
        silver_data (dict): Silver price data keyed by date
    
    Returns:
        list: List of merged data with last 12 months
    """
    # Find common dates
    common_dates = set(gold_data.keys()) & set(silver_data.keys())
    
    if not common_dates:
        return []
    
    # Sort by date and get last 12 months
    sorted_dates = sorted(common_dates, reverse=True)[:12]
    sorted_dates = sorted(sorted_dates)  # Re-sort ascending
    
    merged = []
    for date in sorted_dates:
        merged.append({
            'date': date,
            'gold_price': float(gold_data[date].get('4. close', 0)),
            'silver_price': float(silver_data[date].get('4. close', 0))
        })
    
    return merged


def clear_old_cache(days=30):
    """
    Clear cached data older than specified days.
    
    Args:
        days (int): Remove data older than this many days
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        CommodityData.query.filter(CommodityData.fetched_at < cutoff_date).delete()
        db.session.commit()
        print(f'Cleared cache data older than {days} days')
    except Exception as e:
        print(f'Error clearing cache: {str(e)}')
        db.session.rollback()
