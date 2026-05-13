# Portfolio Team (Collaborative Crypto Portfolio)

## Overview
### Problem
- **Who is affected?**: Small crypto investment teams, study groups, or trading clubs who want a shared way to track their collective and individual performance.
- **What is the issue?**: Most crypto trackers are for solo use. Teams have to use messy spreadsheets to see how everyone is doing together, leading to data entry errors and a lack of real-time visibility into the team's total health.

### Outcome
- **What was achieved?**:

| Objective | Solution | Result |
| :--- | :--- | :--- |
| Shared team performance tracking | Multi-user login and dashboard with aggregate stats | Success |
| Real-time price updates for all members | Custom CoinGecko Pro SDK integration | Success |
| Efficient analytical data storage | DuckDB for collaborative SQL operations | Success |
| High-performance charting | TradingView & Chart.js for team visuals | Success |

- **Measurable results (if any)**: A fully functional collaborative platform where multiple users can contribute to a single team portfolio, with per-member coin limits and real-time aggregate performance analytics.

---

## Demo
Our solution makes tracking crypto as a team simple and visual:
1.  **Join the Team:** Register your account and log in to your personal dashboard.
2.  **Add Your Picks:** Search for a coin (like Bitcoin), enter your trade details, and save. You have 5 slots to showcase your best ideas!
3.  **See the Big Picture:** The main screen automatically shows the team's total value and overall profit/loss.
4.  **Compare & Contrast:** Use the interactive charts to see who's leading the pack or how the team's balance has changed over time.

| Welcome Screen | Team Dashboard |
| :--- | :--- |
| ![Login Screen](assets/screenshot_login.png) | ![Dashboard Overview](assets/screenshot_team_0.png) |

| Performance Trends | Detailed Tables |
| :--- | :--- |
| ![Team Performance](assets/screenshot_team_1.png) | ![Team Portfolio](assets/screenshot_team_2.png) |

---

## Technology Stack
### Frontend components:
- **HTML/CSS/JS**: The core building blocks used to create a clean, responsive team dashboard with dark-mode aesthetics.
- **TradingView Lightweight Charts**: Used to visualize team-wide performance history with professional-grade interactive graphs.
- **Chart.js**: Powering the categorical visualizations, such as asset allocation doughnut charts and member performance bar charts.

### Backend components:
- **Python & FastAPI**: The high-performance "brain" that manages multi-user authentication, collaborative trade processing, and real-time market data.
- **DuckDB**: A super-fast analytical database used to securely store and aggregate trade data from all team members simultaneously.
- **CoinGecko Pro API**: Our trusted source for fetching accurate, professional-level cryptocurrency market data for the entire team.

---

## Development Approach with AI
- **List of AI tools, services, models, and their purposes**:
  - **Antigravity (Gemini 3.1 Pro)**: Our primary AI partner for architecting the collaborative multi-user system, handling backend database migrations, and polishing the frontend UI.
- **List of AI agents, including roles and skills**:
  - **Antigravity Agent**: Acted as a fullstack lead developer, managing everything from secure JWT authentication logic to complex analytical SQL queries in DuckDB.
- **List of key prompts used**:
  - "Migrate the solo portfolio dashboard to a collaborative multi-user platform tracking aggregate team holdings."
  - "Enforce a per-member coin limit (maximum 5 coins) to encourage focused team investing."
  - "Implement a visual layout with side-by-side bar charts and multi-series line charts for team member comparison."
- **List of key review points and the corresponding decision made**:
  - *Review Point*: How to handle shared vs. individual views? *Decision*: We prioritized a "Team First" dashboard that shows aggregate totals at the top, with individual member contributions clearly visible in the charts and tables for transparency.
  - *Review Point*: How to ensure secure access? *Decision*: We implemented a strict JWT-based authentication flow, ensuring that while the dashboard is collaborative, every trade is tied to a verified user account.

---

## Installation
Steps to download and set up the project on your computer:
```bash
# 1. Download the team project code
git clone https://github.com/cloudostrich/cryptoportfolio_team.git
# 2. Open the project folder
cd cryptoportfolio_team
# 3. Create a clean workspace for Python
python3 -m venv .venv
```

Steps to run the project for the first time:

```bash
# 1. Turn on your Python workspace
source .venv/bin/activate

# 2. Install the necessary team-collaboration tools
pip install -r requirements.txt

# 3. Set up the local analytical database for the team
python -m src.backend.db.init_db
```

---

## Usage
How to start and use the application:

```bash
source .venv/bin/activate

# Start the collaborative backend server
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```
- Open `http://localhost:8000` in your web browser.
- Register a new account or log in to join the team dashboard.
- Search for coins, log your trades, and watch the aggregate team statistics update in real-time.
- *For advanced users*: Review the team's API structure and interact with the data programmatically at `http://localhost:8000/docs`.

---

## Project Structure
- `.agents/`: Stores prompts and memory used by the AI agent to manage the collaborative codebase.
- `assets/`: Directory for screenshots and media showing the team dashboard in action.
- `Reference_Materials/`: Collection of external guides and project requirements (like the B1 Builders Programme specs).
- `src/backend/`: The multi-user "brain" handling auth, collaborative logic, and data aggregation.
- `src/frontend/` & `data/`: The visual interface and the secure local folder where the team's shared DuckDB file is kept.
- `tests/`: Automated checks ensuring the team tracker stays reliable for everyone.

---

## Reflection
- **What worked**: Integrating DuckDB allowed us to run lightning-fast analytical queries on shared team data. The per-member coin limit successfully turned the tracker into a strategic tool rather than just a simple list.
- **What failed**: Our initial transition to a multi-user system had a bug where charts would try to load before the user was fully identified, causing empty graphs.
- **Changes made**: We refactored the frontend to strictly wait for the "Who am I?" check before loading any portfolio data.
- **Rationale**: This ensures a secure, smooth experience where every member sees the team's status accurately as soon as they log in.


