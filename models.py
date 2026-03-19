"""
SQLAlchemy models for Regret Meter database.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class UserInput(db.Model):
    """Model to store user inputs and calculated regret scores."""
    __tablename__ = 'user_inputs'
    
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)  # Takeout price (in currency)
    category = db.Column(db.String(50), nullable=False)  # Food category
    delivery_option = db.Column(db.String(20), nullable=False)  # 'delivery' or 'pickup'
    home_price = db.Column(db.Float, nullable=False)  # Home-cooked price
    delivery_fee = db.Column(db.Float, nullable=False)  # Delivery fee (0 or 50)
    difference_saved = db.Column(db.Float, nullable=False)  # Price difference
    commodity_growth = db.Column(db.Float, nullable=False)  # Commodity growth percentage
    regret_score = db.Column(db.Float, nullable=False)  # Final regret score (0-100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserInput {self.id}: {self.category} - Regret Score {self.regret_score}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'price': self.price,
            'category': self.category,
            'delivery_option': self.delivery_option,
            'home_price': self.home_price,
            'delivery_fee': self.delivery_fee,
            'difference_saved': self.difference_saved,
            'commodity_growth': self.commodity_growth,
            'regret_score': self.regret_score,
            'created_at': self.created_at.isoformat()
        }


class CommodityData(db.Model):
    """Model to cache commodity price data from Alpha Vantage API."""
    __tablename__ = 'commodity_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)  # 'GLD' for gold or 'SLV' for silver
    date = db.Column(db.String(10), nullable=False)  # Date in YYYY-MM-DD format
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=True)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    db.UniqueConstraint('symbol', 'date', name='unique_symbol_date')
    
    def __repr__(self):
        return f'<CommodityData {self.symbol} on {self.date}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'symbol': self.symbol,
            'date': self.date,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'volume': self.volume,
            'fetched_at': self.fetched_at.isoformat()
        }
