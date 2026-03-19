# Frontend Requirements for Takeout vs Cooking Regret Meter

## Goals (Frontend only)
- Collect user input: takeout price, category, delivery option.
- Show calculated results: regret score, narrative tag, details.
- Visualize 12-month commodity scenario (gold + silver) via interactive chart.
- Keep UI responsive, accessible, and mobile-friendly.

## Pages/Routes (implemented in Flask backend, frontend templates here)
1. `/` (home)
   - form inputs
2. `/result` (result page)
   - score display
   - chart(s)
   - summary text

## UI Elements
- Input form (Jinja2 + HTML):
  - `amount` number input (required, min=0.01)
  - `category` select dropdown (burgers, pizza, chinese, coffee, other)
  - `delivery` select dropdown (pickup, delivery)
  - submit button
- Result block:
  - large, color-coded regret score
  - textual insight (e.g., "High regret: you could have had RX return")
- Chart area:
  - line chart with 12 months data for gold and silver
  - tooltip with per-month invested gain simulation
- Optional: breadcrumb, status badge, reset button, data source footnote.

## Dynamic Data Binding
- Backend passes via Jinja2 context:
  - `regret_score`, `regret_level`, `amount`, `category`, `delivery`, `commodity_data` (JSON), `monthly_gains`.
- Frontend (JavaScript):
  - parse commodity data for Chart.js
  - set tooltip formatter to include effective gain for the user amount

## Visual style and accessibility
- Theme: green/amber/red spectrum for regret intensity.
- Contrasting text and high legibility.
- Responsive container for mobile/tablet/desktop.
- Form labels and aria attributes.

## Interaction and validation (frontend)
- HTML5 for required fields and pattern.
- Custom JS validation for negative amounts.
- Show inline error messages.

## Dependencies
- Chart.js (or equivalent high-level chart library).
- optional: Tailwind or vanilla CSS.
- optional: Alpine.js/simple JS for interactivity.

## Acceptance criteria
- Form accepts valid input and redirects to results.
- Result page renders score, category and chart.
- Chart has 12 data points, hover details, and legend.
- Regret level computed from values and visually indicated.
