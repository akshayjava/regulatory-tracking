## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.

## 2025-02-28 - [Redundant endpoints hide performance issues]
**Learning:** The application implements duplicate endpoints for the same logical resources (e.g., `/alerts/deadlines` in `alerts.py` and `/regulations/alerts/deadlines` in `regulations.py`). Optimizing one (which was already done for `regulations.py`) leaves the other unoptimized and vulnerable to N+1 queries.
**Action:** When fixing performance bottlenecks like N+1 queries in a specific domain, always search the codebase for redundant or aliased endpoints that may share the same unoptimized data access patterns.
