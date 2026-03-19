"""
Calculations engine for regret score computation.
"""


def calculate_regret_score(difference_saved, takeout_price, commodity_growth):
    """
    Calculate regret score (0-100) based on opportunity cost.
    
    Formula: Regret Score = min(100, ((Difference Saved / Takeout Price) * 100) + (Commodity Growth Percentage / 2))
    
    Factors:
    - Relative savings ratio: How much money saved relative to takeout price
    - Growth potential: How much the commodity could have grown
    
    Args:
        difference_saved (float): Money saved by cooking at home (takeout_price - home_price - delivery_fee)
        takeout_price (float): Original takeout price
        commodity_growth (float): Percentage growth of commodity over 12 months
    
    Returns:
        float: Regret score between 0 and 100
    """
    if takeout_price <= 0:
        return 0
    
    # Factor 1: Relative savings ratio
    savings_ratio = (difference_saved / takeout_price) * 100 if difference_saved > 0 else 0
    
    # Factor 2: Commodity growth contribution (scaled by 0.5)
    growth_factor = commodity_growth / 2
    
    # Combine factors and cap at 100
    regret_score = min(100, savings_ratio + growth_factor)
    
    # Ensure non-negative
    regret_score = max(0, regret_score)
    
    return round(regret_score, 2)


def simulate_investment(difference_saved, monthly_commodity_data):
    """
    Simulate monthly investment returns if the saved money was invested in commodities.
    
    Args:
        difference_saved (float): Amount saved monthly
        monthly_commodity_data (list): List of dicts with 'date' and commodity prices
    
    Returns:
        list: List of investment values at each month
    """
    if not monthly_commodity_data or difference_saved <= 0:
        return []
    
    investment_values = []
    cumulative_shares = 0
    initial_price = None
    
    # Sort data by date
    sorted_data = sorted(monthly_commodity_data, key=lambda x: x['date'])
    
    for i, data_point in enumerate(sorted_data):
        # Average price of gold and silver
        avg_price = (data_point.get('gold_price', 0) + data_point.get('silver_price', 0)) / 2
        
        if avg_price == 0:
            continue
        
        if i == 0:
            initial_price = avg_price
        
        # Buy shares with the difference saved
        shares_bought = difference_saved / avg_price
        cumulative_shares += shares_bought
        
        # Current value
        current_value = cumulative_shares * avg_price
        
        investment_values.append({
            'date': data_point['date'],
            'current_value': round(current_value, 2),
            'shares_held': round(cumulative_shares, 4),
            'avg_price': round(avg_price, 2)
        })
    
    return investment_values


def calculate_regret_level(regret_score):
    """
    Determine regret level based on score.
    
    Args:
        regret_score (float): Score from 0-100
    
    Returns:
        str: Regret level descriptor
    """
    if regret_score >= 75:
        return "Very High Regret"
    elif regret_score >= 50:
        return "High Regret"
    elif regret_score >= 25:
        return "Moderate Regret"
    elif regret_score > 0:
        return "Low Regret"
    else:
        return "No Regret"


def calculate_monthly_gains(initial_investment, monthly_prices):
    """
    Calculate monthly gains if investing the difference saved.
    
    Args:
        initial_investment (float): Amount to invest each month
        monthly_prices (list): List of dicts with 'date' and price data
    
    Returns:
        list: List of monthly gain data
    """
    if not monthly_prices or initial_investment <= 0:
        return []
    
    gains = []
    cumulative_investment = 0
    initial_price = None
    
    sorted_data = sorted(monthly_prices, key=lambda x: x['date'])
    
    for i, price_data in enumerate(sorted_data):
        if initial_price is None:
            initial_price = price_data.get('price', 0)
        
        current_price = price_data.get('price', 0)
        cumulative_investment += initial_investment
        
        if initial_price > 0:
            price_change_percent = ((current_price - initial_price) / initial_price) * 100
            monthly_gain = (cumulative_investment * price_change_percent) / 100
        else:
            monthly_gain = 0
        
        gains.append({
            'date': price_data.get('date'),
            'monthly_gain': round(monthly_gain, 2),
            'price_change_percent': round(price_change_percent, 2) if initial_price > 0 else 0
        })
    
    return gains
