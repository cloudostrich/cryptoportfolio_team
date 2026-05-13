# Portfolio Team

## Overview
### Problem
- **Who is affected?** Crypto investment teams, study groups, or small trading desks.
- **What is the issue?** Teams lack a unified platform to track shared crypto portfolios, compare individual member performance, and manage allocations collaboratively. Existing tools are often geared toward solo investors or are overly complex and expensive for small groups.

### Outcome
- **What was achieved?** Developed a collaborative team crypto portfolio tracker where multiple users can log in, add trades (up to a 5-coin limit per member), and view real-time team and individual performance through interactive charts. 
- **Measurable results (if any).** Successfully integrated multi-user authentication, combined team-wide portfolio calculations, and interactive visualisations into a single cohesive dashboard.

---

## Demo
- **How does the solution work from the user’s perspective?**
  1. Users log in or register an account.
  2. Each member can search for coins and add their buy/sell trades, limited to 5 unique coins per member to encourage focused investing.
  3. The main dashboard displays aggregate team statistics (Total Value, Team PnL) alongside the individual user's statistics.
  4. Interactive charts allow users to toggle between historical performance and asset allocation, with breakdowns of team vs. individual member contributions.
  5. The team holdings and trade history tables provide a transparent view of all team actions.

**Screenshots:**
![Login Screen](assets/screenshot_login.png)
![Dashboard Overview](assets/screenshot_team_0.png)
![Team Performance Charts](assets/screenshot_team_1.png)
![Team Portfolio Table](assets/screenshot_team_2.png)

---

## Technology Stack
### Frontend components:
- **Vanilla HTML5 / CSS3** for structure and styling.
- **Vanilla JavaScript (ES6 Modules)** for API interaction and DOM manipulation.
- **TradingView Lightweight Charts** for high-performance financial time-series charts.
- **Chart.js** for categorical data visualisations (e.g., allocation doughnut charts, member performance bar charts).

### Backend components:
- **Python 3 & FastAPI** for a high-performance asynchronous REST API.
- **DuckDB** for fast, embedded, analytical SQL database operations.
- **bcrypt + python-jose** for secure JWT-based authentication.
- **CoinGecko Pro API** (via custom SDK integration) for real-time and historical market data.

---

## Development Approach with AI
- **List of AI tools, services, models, and their purposes:**
  - **Gemini 3.1 Pro:** Used as the primary AI pair-programmer for architectural decisions, backend logic (FastAPI, DuckDB), frontend structure, and debugging complex state issues.
  - **Cursor / GitHub Copilot:** Used for inline code completion and boilerplate generation.
- **List of AI agents, including roles and skills:**
  - **Antigravity (Coding Assistant):** Provided end-to-end fullstack development, reading/writing codebase files, running terminal tests, and performing root-cause analysis.
- **List of key prompts used:**
  - *"Migrate the solo portfolio dashboard to a collaborative multi-user platform tracking aggregate team holdings."*
  - *"Enforce a per-member coin limit (maximum 5 coins)."*
  - *"Implement a visual layout with side-by-side bar charts and multi-series line charts for team member comparison."*
- **List of key review points and the corresponding decision made:**
  - *Review Point:* Shared vs. Isolated portfolios. *Decision:* Display aggregate team data at the top, with individual contributions visibly delineated in the charts and tables to foster healthy competition and transparency.
  - *Review Point:* Frontend authentication state. *Decision:* Moved from parallel unauthenticated API fetches to a strict `fetchMe()` sequence to resolve 401 errors and ensure proper user session management.

---

## Installation
Steps to setup the project workspace:
1. Clone the project:
   ```bash
   git clone https://github.com/cloudostrich/cryptoportfolio_team.git
   ```
2. Change directory to project:
   ```bash
   cd cryptoportfolio_team
   ```
3. Setup the python virtual environment:
   ```bash
   python3 -m venv .venv
   ```

Steps to run the project.

1. Navigate to the project root:
   ```bash
   cd portfolio-team
   ```
2. Activate the virtual environment and install dependencies:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Initialise the DuckDB database:
   ```bash
   python -m src.backend.db.init_db
   ```
4. Start the backend server:
   ```bash
   uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Usage
- **Access the Dashboard:** Open `http://localhost:8000` in your web browser.
- **Register/Login:** Create a new team member account or log in with existing credentials.
- **Add Trades:** Search for a coin (e.g., "Bitcoin"), enter the amount and price, and click "Add Trade". Note the 5-coin limit per member.
- **Analyse Data:** Toggle between the "History" line chart and "Allocation" pie chart to see how individual assets and members contribute to the overall team portfolio. Use the timeframe tabs to view 24h, 7d, 30d, or 90d history.

---

## Project Structure
- `src/frontend/` — Contains all client-side code (`index.html`, CSS styling, and modular JS scripts for API and Chart logic).
- `src/backend/` — Contains the FastAPI application, divided into `routes/`, `services/`, `models/`, and `db/` (DuckDB interactions).
- `data/` — Stores the embedded `portfolio.duckdb` database file.
- `tests/` — Contains `pytest` test suites for ensuring backend reliability.
- `Reference_Materials/` — Contains project specifications and related documentation.

---

## Reflection
- **What worked:** Integrating DuckDB provided incredibly fast analytical queries, which made calculating aggregate team summaries and individual performance very efficient. The move from a "Thesis Board" to a unified team tracker simplified the user flow significantly.
- **What failed:** Initially, the frontend was making API calls without verifying authentication status, resulting in a race condition and `401 Unauthorized` errors when transitioning from the solo project to the team project.
- **Changes made, rationale:** We refactored `app.js` to strictly await the `fetchMe()` authentication check before attempting to load the dashboard data (`loadDashboard()`). We also changed the visual approach from individual thesis cards to a comprehensive team-wide data table and chart layout to better serve the collaborative goal.
