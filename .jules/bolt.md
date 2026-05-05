## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.
## 2025-03-05 - Duplicate endpoints causing missed optimizations
**Learning:** This codebase sometimes has redundant or duplicate endpoints serving similar data (e.g., `/alerts/deadlines` and `/regulations/alerts/deadlines`). An optimization (N+1 query fix using `GROUP_CONCAT`) was applied to one but missed in the duplicate endpoint.
**Action:** When finding a performance issue or optimizing an endpoint, always grep the codebase for similar database queries or redundant routes to ensure the optimization is applied globally.
