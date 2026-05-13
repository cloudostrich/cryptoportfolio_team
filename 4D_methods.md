# 4D Methodology: Portfolio Team Project

This document outlines how the **Portfolio Team** collaborative crypto tracking project was conceptualised and built using the 4D Design Innovation Methodology (Discover, Define, Develop, Deliver) as outlined in the DI Design Method Cards.

## 1. Discover
**Mindset: Empathy**

The Discover phase focuses on empathising with end-users and understanding their core needs and concerns in realistic contexts.
- **Who are our users?** Crypto investment teams, study groups, and collaborative trading desks.
- **What are their needs?** They need a unified platform to track shared portfolios, hold each other accountable, and compare individual trading performance without dealing with overly complex or expensive enterprise tools.
- **Key Insight & Context:** Through contextual needs analysis, we discovered that users often resort to sharing cumbersome spreadsheets to track group investments. A major pain point is the lack of transparency regarding who bought what, and how individual trading decisions affect the overall team's Profit and Loss (PnL).

## 2. Define
**Mindset: Interpretation & Reframing**

In the Define phase, we made sense of our discoveries and mapped them into clear product specifications, functions, and opportunity statements.
- **Opportunity Statement:** How might we design a collaborative dashboard that tracks team-wide crypto holdings while clearly delineating individual member contributions and performance?
- **Core Requirements Defined:**
  - Secure, multi-user authentication system to separate individual identities.
  - A 5-coin limit per member to encourage focused, high-conviction investing rather than over-diversification.
  - Real-time PnL calculation aggregating individual trades into a team-wide summary.
  - Clear visualizations comparing team totals vs. individual member metrics.

## 3. Develop
**Mindset: Joyfulness & Ideation**

During the Develop phase, we ideated and modeled concepts based on the identified opportunities to define design criteria and depth.
- **Ideation & Concept Generation:** We explored different dashboard layouts. While initially considering a "thesis board" with individual pitch cards, we pivoted to a unified data table and charting system, which provides much more effective analytical insights at a glance.
- **Design Criteria:** The interface needed to feature a modern "dark mode" aesthetic for extended screen time, be highly responsive, and present data densely but cleanly.
- **Solution Selection:** We chose to build the frontend using Vanilla JS and HTML/CSS for complete structural control. For the backend, we selected FastAPI (Python) and DuckDB for ultra-fast, embedded analytical SQL queries, alongside TradingView Lightweight Charts and Chart.js for premium data visualization.

## 4. Deliver
**Mindset: Non-attachment & Iteration**

The Deliver phase involves iteratively prototyping, testing concepts, and reducing the risk of failure during deployment.
- **Prototyping & Testing:** We built the core backend logic first, heavily utilizing AI pair-programming to rapidly scaffold the DuckDB schemas and FastAPI routing. We then created wireframes and iterative prototypes of the frontend dashboard.
- **Iterative Refinement:** During integration testing, we encountered architectural challenges, such as frontend race conditions causing `401 Unauthorized` errors when transitioning from a solo-user model to a multi-user model. By maintaining non-attachment to the initial code, we swiftly refactored the frontend logic to enforce strict sequential loading (verifying authentication before fetching dashboard data).
- **Final Solution:** The result is a robust, working prototype that successfully delivers on the defined opportunity statement, ready for further real-world usability testing and feedback capture.
