## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.
## 2024-05-16 - Redundant N+1 Query Anti-Pattern in Alerts
**Learning:** Found an N+1 query bottleneck in `backend/api/routes/alerts.py` (`get_deadlines`) that iterates over regulations to fetch internal `id`s and then query `regulation_verticals`. This mirrors the duplicate endpoint in `backend/api/routes/regulations.py` (`/alerts/deadlines`) which already had this N+1 issue fixed.
**Action:** When fixing performance bottlenecks (like N+1 queries), always search the codebase for redundant or aliased endpoints that may share the same unoptimized data access patterns.
