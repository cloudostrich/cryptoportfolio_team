---
name: multi-user-auth
description: Guidelines for handling user authentication, session management, and tenant isolation in the multi-user team dashboard.
---

# Goal

Use this skill whenever working on user registration, login, session validation, or multi-user access control.

# When to use

Use this skill when the user asks for:
- User login / logout flow
- Session or JWT validation
- Restricting routes to logged-in users only
- Enforcing tenant isolation in database queries (filtering by user_id)

# Project assumptions

- This is a multi-user collaborative dashboard.
- Users have roles (e.g., analyst).
- Backend routes should be protected to prevent unauthorized access.
- Every user's trades and theses belong strictly to them, though aggregated views (like team holdings) combine data.

# Workflow

1. Always extract the `user_id` from the current authenticated context.
2. When creating a new entity (Trade, Thesis, Vote), attach the `user_id` to the record.
3. When querying private data (like personal holdings), include `WHERE user_id = ?` to enforce tenant isolation.
4. For endpoints that return team aggregated data, ensure data is properly GROUPED and doesn't expose sensitive individual details unless intended by the UI.

# Output expectations

- Secure, protected FastAPI routes.
- DuckDB queries that consistently include `user_id`.

# Constraints

- Never expose another user's private settings or isolated trades unless it is specifically part of a public "Team View" aggregation.
- Never hardcode user IDs.
