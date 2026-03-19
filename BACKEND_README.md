# Regret Meter - Backend Setup & Development Guide

A Flask-based web application that calculates the financial regret score of buying takeout instead of cooking at home. The regret score is based on the opportunity cost of investing the saved money in commodity ETFs (gold and silver).

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   cd fse_mini_hackathon_regret
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up API key** (Optional but recommended)
   - Create a `.env` file in the project root:
     ```
     ALPHA_VANTAGE_API_KEY=your_api_key_here
     ```
   - Get a free API key from: https://www.alphavantage.co/
   - If not provided, the app will use a 'demo' key with limited requests

6. **Run the Flask application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
fse_mini_hackathon_regret/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── calculations.py        # Regret score calculation engine
├── api_handler.py         # Alpha Vantage API integration
├── categories.csv         # Food categories and home prices
├── requirements.txt       # Python dependencies
├── keepinmind.md          # Frontend integration notes
├── regret_meter.db        # SQLite database (auto-created)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_calculations.py    # Unit tests for calculations
│   └── test_app.py             # Integration tests for routes
└── templates/             # (To be created by frontend)
    └── home.html         # (To be created by frontend)
```

## Backend Features

### 1. Regret Score Calculation
- **Formula**: `min(100, ((Difference Saved / Takeout Price) * 100) + (Commodity Growth % / 2))`
- **Factors**:
  - Relative savings ratio (how much money saved)
  - Commodity growth potential (investment opportunity cost)
- **Range**: 0-100 (higher = more regret)

### 2. Commodity Data Integration
- Fetches last 12 months of gold (GLD) and silver (SLV) ETF prices
- Uses Alpha Vantage API (free tier available)
- Implements intelligent caching (24-hour TTL)
- Falls back to cached data if API is unavailable

### 3. Database
- Uses SQLite for simplicity
- Two main tables:
  - `user_inputs`: Stores all user calculations and regret scores
  - `commodity_data`: Caches API responses to reduce API calls

### 4. API Endpoints

#### GET `/`
Returns the home page with input form.

**Response**: HTML template

#### POST `/result`
Calculates regret score and returns analysis data.

**Request Body**:
```json
{
  "price": 200,
  "category": "Burgers",
  "delivery_option": "pickup"
}
```

**Response**:
```json
{
  "regret_score": 45.5,
  "difference_saved": 50,
  "commodity_growth": 12.5,
  "graph_data": [
    {
      "date": "2025-01-01",
      "gold_price": 150.25,
      "silver_price": 25.50,
      "monthly_gain": 12.5
    }
  ],
  "category": "Burgers",
  "takeout_price": 200,
  "home_price": 150,
  "delivery_fee": 0
}
```

**Error Responses**:
- 400: Missing required fields or invalid input
- 500: Server-side calculation error

## Configuration

### Categories
Food categories and their home-cooked prices are stored in `categories.csv`:

```csv
category,home_price
Burgers,150
Pizza,120
Chinese,140
Coffee,25
...
```

Edit this file to add/modify categories.

### Delivery Fee
- Currently hardcoded to 50 currency units for delivery
- 0 currency units for pickup
- To modify, edit the `result()` function in `app.py`

### API Configuration
- Symbol: GLD (Gold ETF) and SLV (Silver ETF)
- Endpoint: TIME_SERIES_MONTHLY
- Cache: 24 hours
- API Key: Set via environment variable `ALPHA_VANTAGE_API_KEY`

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_calculations.py
```

Run with verbose output:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage
- **test_calculations.py**: Unit tests for regret score formulas and investment simulations
- **test_app.py**: Integration tests for Flask routes, database persistence, and API error handling

## Troubleshooting

### Issue: "No module named 'flask'"
- **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Issue: "ALPHA_VANTAGE_API_KEY not found"
- **Solution**: The app will use 'demo' key. Create `.env` file with your API key for production use.

### Issue: Database lock errors
- **Solution**: Delete `regret_meter.db` and restart the app to recreate fresh database

### Issue: API rate limit exceeded
- **Solution**: The app will use cached data. Wait 1 minute or upgrade Alpha Vantage API plan.

### Issue: Port 5000 already in use
- **Solution**: Change port in `app.py` line: `app.run(debug=True, host='127.0.0.1', port=5001)`

## Development Workflow

1. **Make changes** to Python files
2. **Run tests** to validate changes: `pytest tests/`
3. **Test manually** by making requests to endpoints
4. **Check for errors** using Flask debug mode

### Example Manual Testing

Start Flask app:
```bash
python app.py
```

In another terminal, test the endpoint:
```bash
curl -X POST http://localhost:5000/result \
  -H "Content-Type: application/json" \
  -d '{"price": 200, "category": "Burgers", "delivery_option": "pickup"}'
```

## Frontend Integration

See `keepinmind.md` for:
- Frontend dependencies on backend
- Required HTML/CSS/JS structure
- Integration checklist
- Data flow diagram

## Key Database Queries

Query all user calculations:
```python
from app import app
from models import db, UserInput

with app.app_context():
    all_inputs = UserInput.query.all()
    for inp in all_inputs:
        print(f"{inp.category}: Score {inp.regret_score}")
```

Query average regret score by category:
```python
with app.app_context():
    from sqlalchemy import func
    avg_scores = db.session.query(
        UserInput.category,
        func.avg(UserInput.regret_score).label('avg_score')
    ).group_by(UserInput.category).all()
```

## Performance Considerations

1. **API Caching**: Commodity data is cached for 24 hours to reduce API calls
2. **Database Indexing**: Consider adding indexes for frequent queries (category, regret_score)
3. **Rate Limiting**: Alpha Vantage free tier allows 5 requests per minute
4. **Lazy Loading**: Implement pagination for large result sets in future versions

## Security Notes

⚠️ **Important for Production**:
- Never commit `.env` file with API keys
- Add `.env` to `.gitignore`
- Change Flask `debug=False` for production
- Validate all user inputs (currently basic validation only)
- Use environment variables for sensitive data
- Consider adding CORS headers if frontend is separate domain

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database
- **SQLAlchemy**: Database toolkit
- **requests**: HTTP library for API calls
- **pytest**: Testing framework
- **python-dotenv**: Environment variable management

## Deployment

For production deployment:

1. **Set `debug=False`** in app.py
2. **Use production WSGI server** (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. **Set up environment variables** for API keys
4. **Use PostgreSQL** instead of SQLite for production
5. **Add error logging** (Sentry, etc.)

## License

[Add your project license here]

## Contributing

[Add contribution guidelines here]

## Further Development

### Planned Features
- [ ] User authentication
- [ ] Save and view calculation history
- [ ] Multiple currency support
- [ ] PDF report generation
- [ ] Advanced commodity analytics
- [ ] Machine learning for price predictions

### Known Limitations
- Single commodity strategy (can add bonds, stocks, etc.)
- Assumes equal monthly investment
- No tax calculations
- No transaction costs included
