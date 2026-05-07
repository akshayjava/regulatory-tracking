## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.
## 2024-05-24 - N+1 Query Anti-Pattern in Loop using SQLite GROUP_CONCAT
**Learning:** Instead of executing separate subqueries inside loops to fetch relationships (like `regulation_verticals`), using `GROUP_CONCAT` combined with `LEFT JOIN` in SQLite solves the N+1 problem and provides significant speedup (~3x faster).
**Action:** Always check loop queries for related data fetching. Replace loop queries with `LEFT JOIN` and `GROUP_CONCAT` when appropriate.
