# Overlap with Frontend and Project Scope

This file collects items in the plan that directly overlap frontend deliverables.

## Data display + layout (frontend-driven)
- Regret score section (0-100) with color tier labels.
- Graph section for commodities (gold/silver) with hover details.
- Category and delivery options should be part of form UI.

## Requirements that need frontend+backend teaming
- sending user input (amount, category, delivery) to Flask `/result`.
- receiving `commodity_data` JSON from backend to render chart.
- client-side validation and UX feedback for missing or invalid input.
- styling to match the "regret meter" concept (low/high risk states).

## Notes for integration
- Backend must expose templating context keys used by frontend (e.g., `rate_series`, `regret_score`).
- Keep the chart data shape stable (e.g., `{month, gold, silver, cumulative_gain}`) for direct use by JS.
- If backend uses static files (CSS/JS), put in `static/css` and `static/js`, and reference in Jinja templates.
