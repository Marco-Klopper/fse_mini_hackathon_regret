"""
Calculations engine for regret score computation.
"""


def calculate_regret_score(difference_saved, takeout_price, commodity_growth):
    """
    Calculate regret score (0-100) based on opportunity cost.

    Formula: Regret Score = min(100, ((Difference Saved / Takeout Price) * 100) + (Commodity Growth Percentage / 2))

    Args:
        difference_saved (float): Money saved by cooking at home (takeout_price - home_price - delivery_fee)
        takeout_price (float): Original takeout price
        commodity_growth (float): Percentage growth of investment over 12 months

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


def _extract_gold_price(data_point):
    """Extract gold price from a data point."""
    if 'gold_price' in data_point:
        return float(data_point.get('gold_price', 0))
    if 'price' in data_point:
        return float(data_point.get('price', 0))
    # Fallback: average of gold and silver if both present (legacy)
    gold = float(data_point.get('gold_price', 0) or 0)
    silver = float(data_point.get('silver_price', 0) or 0)
    return (gold + silver) / 2


def simulate_investment(difference_saved, monthly_commodity_data):
    """
    Simulate monthly investment returns if the saved money was invested in gold.

    Args:
        difference_saved (float): Amount saved each month
        monthly_commodity_data (list): List of dicts with 'date' and 'gold_price'

    Returns:
        list: List of investment snapshots for each month
    """
    if not monthly_commodity_data or difference_saved <= 0:
        return []

    investment_values = []
    total_shares = 0.0
    total_invested = 0.0

    # Sort by date chronologically
    sorted_data = sorted(monthly_commodity_data, key=lambda x: x['date'])

    for data_point in sorted_data:
        price = _extract_gold_price(data_point)
        if price <= 0:
            continue

        total_invested += difference_saved
        shares_bought = difference_saved / price
        total_shares += shares_bought

        current_value = total_shares * price
        total_gain = current_value - total_invested
        gain_percent = (total_gain / total_invested) * 100 if total_invested > 0 else 0

        investment_values.append({
            'date': data_point['date'],
            'gold_price': round(price, 2),
            'total_invested': round(total_invested, 2),
            'current_value': round(current_value, 2),
            'total_gain': round(total_gain, 2),
            'gain_percent': round(gain_percent, 2),
            'shares_held': round(total_shares, 6)
        })

    return investment_values


def calculate_commodity_growth(investment_data):
    """Calculate overall growth percentage for the investment data."""
    if not investment_data:
        return 0

    last = investment_data[-1]
    return last.get('gain_percent', 0)


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
