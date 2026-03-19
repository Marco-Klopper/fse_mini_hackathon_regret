"""
Unit tests for calculations module.
"""
import pytest
from calculations import (
    calculate_regret_score,
    simulate_investment,
    calculate_regret_level,
    calculate_monthly_gains
)


class TestCalculateRegretScore:
    """Test regret score calculation."""
    
    def test_positive_savings_with_growth(self):
        """Test regret score with positive savings and commodity growth."""
        score = calculate_regret_score(
            difference_saved=100,
            takeout_price=200,
            commodity_growth=10
        )
        # (100/200)*100 + 10/2 = 50 + 5 = 55
        assert score == 55.0
    
    def test_negative_savings_no_regret(self):
        """Test regret score when no money was saved."""
        score = calculate_regret_score(
            difference_saved=-50,
            takeout_price=200,
            commodity_growth=5
        )
        # Negative savings treated as 0, so only commodity_growth/2
        assert score == 2.5
    
    def test_high_savings_high_growth_capped_at_100(self):
        """Test that regret score is capped at 100."""
        score = calculate_regret_score(
            difference_saved=500,
            takeout_price=200,
            commodity_growth=150
        )
        # Would be (500/200)*100 + 150/2 = 250 + 75 = 325, but capped at 100
        assert score == 100.0
    
    def test_zero_takeout_price(self):
        """Test with zero takeout price."""
        score = calculate_regret_score(
            difference_saved=100,
            takeout_price=0,
            commodity_growth=5
        )
        assert score == 0
    
    def test_negative_commodity_growth(self):
        """Test with negative commodity growth."""
        score = calculate_regret_score(
            difference_saved=100,
            takeout_price=200,
            commodity_growth=-20
        )
        # (100/200)*100 + (-20/2) = 50 - 10 = 40
        assert score == 40.0


class TestCalculateRegretLevel:
    """Test regret level descriptor."""
    
    def test_very_high_regret(self):
        assert calculate_regret_level(80) == "Very High Regret"
        assert calculate_regret_level(100) == "Very High Regret"
    
    def test_high_regret(self):
        assert calculate_regret_level(60) == "High Regret"
        assert calculate_regret_level(50) == "High Regret"
    
    def test_moderate_regret(self):
        assert calculate_regret_level(40) == "Moderate Regret"
        assert calculate_regret_level(25) == "Moderate Regret"
    
    def test_low_regret(self):
        assert calculate_regret_level(10) == "Low Regret"
        assert calculate_regret_level(1) == "Low Regret"
    
    def test_no_regret(self):
        assert calculate_regret_level(0) == "No Regret"


class TestSimulateInvestment:
    """Test investment simulation."""
    
    def test_investment_with_positive_growth(self):
        """Test investment simulation with commodity price growth."""
        monthly_data = [
            {'date': '2025-01-01', 'gold_price': 100, 'silver_price': 10},
            {'date': '2025-02-01', 'gold_price': 110, 'silver_price': 11},
            {'date': '2025-03-01', 'gold_price': 120, 'silver_price': 12}
        ]

        result = simulate_investment(50, monthly_data)

        assert len(result) == 3
        assert result[0]['current_value'] == 50.0
        assert result[0]['total_invested'] == 50.0
        assert result[0]['gain_percent'] == 0.0
        assert result[1]['current_value'] == 55.0
        assert result[1]['gain_percent'] == 10.0
        assert result[2]['current_value'] == 60.0
        assert result[2]['gain_percent'] == 20.0
    
    def test_investment_with_zero_difference(self):
        """Test investment simulation with zero difference saved."""
        monthly_data = [
            {'date': '2025-01-01', 'gold_price': 100, 'silver_price': 10}
        ]
        
        result = simulate_investment(0, monthly_data)
        assert result == []
    
    def test_investment_with_empty_data(self):
        """Test investment simulation with no data."""
        result = simulate_investment(50, [])
        assert result == []


class TestCalculateMonthlyGains:
    """Test monthly gains calculation."""
    
    def test_monthly_gains_calculation(self):
        """Test monthly gains with positive price movement."""
        monthly_prices = [
            {'date': '2025-01-01', 'price': 100},
            {'date': '2025-02-01', 'price': 105},
            {'date': '2025-03-01', 'price': 110}
        ]
        
        result = calculate_monthly_gains(25, monthly_prices)
        
        assert len(result) == 3
        assert 'monthly_gain' in result[0]
        assert 'price_change_percent' in result[0]
        assert result[0]['price_change_percent'] == 0  # First month has no change
    
    def test_monthly_gains_with_price_increase(self):
        """Test that gains increase with price movement."""
        monthly_prices = [
            {'date': '2025-01-01', 'price': 100},
            {'date': '2025-02-01', 'price': 110}
        ]
        
        result = calculate_monthly_gains(100, monthly_prices)
        
        # Second month: 10% gain on 200 invested = 20
        assert result[1]['monthly_gain'] == 20.0
        assert result[1]['price_change_percent'] == 10.0
