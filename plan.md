## Takeout vs cooking at home regret meter

### The idea
We want to create a regret meter based on the financial opportunity cost involved by paying higher prices for takeouts than making the food at home.
The difference in price we want simulate an investment in a commodity over 12 months.
The opportunity cost would use the last 12 months of trading information and apply it to the difference saved.
We will use the alphavantage api to get the price.
We would need to define set categories for takeout, eg. burgers, pizza, chinese, coffee etc. The price for home made meals can be determined and stored in a csv file. The user will select the category after inputting the amount.
There needs to be a dropdown specifying delivery or pick up, then a fixed price should be added.

### MVP
Web interface with one section to input the price, and select the food category and delivery option.
The output should be a graph of the last 12 months of the gold and silver commodity index, the user should be able to hover over the graph and see what the gain would have been in monthly periods.
Lastly it should also output the regret score.

### Technical Requirements (from regret.md)
- Flask web app with at least two routes (home and result).
- HTML/CSS with Jinja2 templates.
- SQLAlchemy + SQLite for storing user inputs and calculated regret scores.
- External API: Alpha Vantage for commodity prices (gold and silver).
- Regret Score: 0-100 based on opportunity cost (e.g., what if invested in commodities instead of spending on takeout).
- Formula: Regret Score = min(100, ((Difference Saved / Takeout Price) * 100) + (Commodity Growth Percentage / 2)). Factors: relative savings ratio and growth potential. This ensures at least two factors and scales to 0-100.

### Development Plan
Split into Frontend and Backend. This plan is designed for AI agents to follow step-by-step. Each step includes clear objectives, tools needed, and vibe notes for fun coding.

#### Backend (Flask + Data Handling)
1. **Set up Flask App Structure**
   - Create app.py as main Flask file.
   - Define routes: / (home) for input form, /result for displaying output.
   - Install Flask, SQLAlchemy, requests (for API).
   - Vibe: Get the skeleton running with a "Hello World" to feel the power.

2. **Database Setup with SQLAlchemy**
   - Create models: UserInput (store price, category, delivery, regret score), CommodityData (cache API data with date, gold_price, silver_price).
   - Use SQLite for simplicity.
   - Migrate to store data persistently.
   - Vibe: Think of it as your app's memory bank – no more forgetting!

3. **API Integration (Alpha Vantage)**
   - Use TIME_SERIES_MONTHLY endpoint for symbols GLD (gold ETF) and SLV (silver ETF).
   - Function to fetch last 12 months data, cache in DB.
   - Handle API errors gracefully (e.g., rate limits, invalid keys).
   - Vibe: Unleash the data dragon – watch numbers flow in!

4. **Calculations Engine**
   - Load home-made prices from categories.csv (columns: category, home_price).
   - Delivery fee: fixed R50 for delivery, R0 for pickup.
   - Calculate difference saved: takeout price - home price - delivery fee.
   - Simulate investment: assume investing difference at start of each month in commodities, calculate cumulative growth over 12 months.
   - Compute Regret Score: Use formula above to get 0-100 value.
   - Vibe: Math magic time – turn dollars into regret points!

5. **Backend Testing**
   - Unit tests for calculations and API calls.
   - Ensure routes work and data stores correctly.
   - Vibe: Break it before it breaks you – test like a boss.

#### Frontend (HTML/CSS + Graph)
1. **Basic HTML Form**
   - Input fields: price (number), category (dropdown: burgers, pizza, chinese, coffee), delivery (dropdown: delivery/pickup).
   - Submit to /result.
   - Use Jinja2 for dynamic content.
   - Vibe: Make it pretty – users love shiny interfaces!

2. **Result Page with Graph**
   - Display regret score prominently (e.g., "Regret Score: 75/100 - High Regret!").
   - Embed interactive graph (Chart.js) showing gold/silver prices over 12 months as line charts.
   - Hover tooltips: show monthly gains if invested (e.g., "Month 6: +R150 gain").
   - Vibe: Visualize the pain – graphs that hit hard!

3. **Styling with CSS**
   - Responsive design, fun colors (regret theme: red for high, green for low).
   - Ensure mobile-friendly.
   - Vibe: Style it up – make regret look cool!

4. **Frontend Integration**
   - Pass data from backend to templates (e.g., score, graph data as JSON).
   - Handle form validation on frontend (e.g., required fields).
   - Vibe: Connect the dots – frontend meets backend in harmony.

#### Overall Integration and Deployment
1. **Full App Testing**
   - End-to-end: Input -> Calculation -> Display.
   - GitHub repo setup with README.
   - Vibe: Put it all together – MVP achieved!

2. **Demo Prep**
   - Prepare examples: "Should I order pizza or cook?"
   - Show input, graph, score.
   - Vibe: Demo day – impress the judges!

This plan is iterative: build backend first, then frontend. AI agents, follow the steps, use tools like run_in_terminal for setup, and edit files as needed. Let's vibe code this regret machine!

