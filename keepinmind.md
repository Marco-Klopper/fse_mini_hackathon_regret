# Keep in Mind: Backend-Frontend Integration

This document outlines dependencies, blockers, and integration points between the backend and frontend for the Regret Meter application.

## Frontend Dependencies on Backend

### 1. **Home Route (`/`)**
- **Purpose**: Serve the input form page
- **Expected Response**: HTML template with:
  - Input field for takeout price (number)
  - Dropdown for food categories (populated from backend)
  - Dropdown for delivery option (delivery/pickup)
  - Submit button
- **Frontend Responsibility**: 
  - Make POST request to `/result` endpoint with JSON payload
  - Handle form validation before submission

### 2. **Result Route (`/result`)**
- **Method**: POST
- **Input Format**: JSON
  ```json
  {
    "price": 200,
    "category": "Burgers",
    "delivery_option": "pickup"
  }
  ```
- **Output Format**: JSON
  ```json
  {
    "regret_score": 45.5,
    "difference_saved": 50,
    "commodity_growth": 12.5,
    "graph_data": [
      {
        "date": "2025-01-01",
        "gold_price": 150.25,
        "total_invested": 50,
        "current_value": 52.3,
        "total_gain": 2.3,
        "gain_percent": 4.6
      }
    ],
    "category": "Burgers",
    "takeout_price": 200,
    "home_price": 150,
    "delivery_fee": 0
  }
  ```
- **Frontend Responsibility**:
  - Parse JSON response
  - Display regret score prominently
  - Render interactive graph using Chart.js
  - Show hover tooltips with monthly gain data
  - Display color-coded regret level (red for high, green for low)

## Current Blockers

### 1. **Categories CSV File**
- ✅ **RESOLVED**: `categories.csv` is created with default categories (Burgers, Pizza, Chinese, Coffee, Sushi, Mexican, Salad, Fried Chicken, Thai, Indian)
- **Frontend Note**: These are the only available categories unless the CSV is updated

### 2. **API Key Required**
- **Blocker**: Alpha Vantage API key is needed for commodity price data
- **How to Set**: Create a `.env` file in the project root with:
  ```
  ALPHA_VANTAGE_API_KEY=your_api_key_here
  ```
- **Get Free Key**: Sign up at https://www.alphavantage.co/
- **Demo Mode**: Backend will use 'demo' API key if not provided, but with limited requests
- **Frontend Impact**: If API key is invalid or rate-limited, the backend will return fallback cached data (if available)

### 3. **Templates Directory Not Created**
- **Blocker**: Flask expects `templates/home.html` but it doesn't exist yet
- **Frontend Responsibility**: Create the `templates/` directory and `home.html` file
- **Template Engine**: Uses Jinja2
- **Required Variables** in `home.html`:
  - `categories`: List of category objects with `name` and `home_price` fields
  - Form action should POST to `/result`

### 4. **Static Assets Directory Not Created**
- **Frontend Responsibility**: Create `static/` directory for:
  - `css/style.css` - Styling
  - `js/app.js` - Frontend logic
  - Chart.js library for graph rendering

## Integration Checklist

- [ ] Create `templates/` directory
- [ ] Create `templates/home.html` with form
- [ ] Create `static/` directory
- [ ] Add Chart.js to `static/` or use CDN
- [ ] Implement form submission in `static/js/app.js`
- [ ] Parse `/result` JSON response
- [ ] Render graphs with hover tooltips
- [ ] Implement color-coded regret level display
- [ ] Test end-to-end flow
- [ ] Set up Alpha Vantage API key in `.env`

## Data Flow

```
User Input (HTML Form)
    ↓
Frontend JavaScript (form validation)
    ↓
POST /result (JSON payload)
    ↓
Backend: Validate & Calculate
    ↓
Backend: Fetch Commodity Data (API or cache)
    ↓
Backend: Calculate Regret Score & Gains
    ↓
Backend: Store in Database
    ↓
Response: JSON with score, gains, graph data
    ↓
Frontend: Parse & Display Results
    ↓
User Views: Regret Score + Graph
```

## Database

- **Type**: SQLite (`regret_meter.db`)
- **Tables**:
  1. `user_inputs` - Stores all user calculations
  2. `commodity_data` - Caches API responses (24-hour TTL)
- **Frontend Impact**: Frontend doesn't need to interact directly with database (backend handles all persistence)

## Testing Backend

Run tests with:
```bash
pytest tests/
```

Key test files:
- `tests/test_calculations.py` - Unit tests for regret score calculations
- `tests/test_app.py` - Integration tests for Flask routes

## Environment Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` with API key
3. Run Flask app: `python app.py`
4. Backend will be available at `http://localhost:5000`

## API Endpoint Details

### GET `/` 
- Returns HTML form template
- No JSON response

### POST `/result`
- Accepts JSON with price, category, delivery_option
- Returns JSON with scores and graph data
- Error handling:
  - 400: Missing fields or invalid input
  - 500: Server-side calculation error

## Frontend Implementation Notes

1. **Regret Score Display**:
   - Use `calculate_regret_level()` script or implement frontend equivalent
   - Color scheme: Green (0-25), Yellow (25-50), Orange (50-75), Red (75-100)

2. **Graph Display**:
   - X-axis: Dates (last 12 months)
   - Y-axis: Price of gold (GLD)
   - Overlay: Monthly gains on hover
   - Use `graph_data` array from response

3. **Form Validation**:
   - Price must be positive number
   - Category must be from dropdown options
   - Delivery option must be 'delivery' or 'pickup'

4. **Error Handling**:
   - Display user-friendly error messages if API fails
   - Use cached data if available (backend will handle fallback)
   - Show loading state while calculating

## Future Enhancements

- [ ] Add more food categories
- [ ] Support multiple currencies (currently hardcoded to currency units)
- [ ] User authentication and history
- [ ] Generate PDF reports
- [ ] Share results functionality
