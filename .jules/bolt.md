## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.
## 2026-05-01 - [Batch Query optimization for alerts endpoint]
**Learning:** Found an N+1 query vulnerability in the `/alerts/deadlines` endpoint. By utilizing `GROUP_CONCAT` and `LEFT JOIN` inside `backend/api/routes/alerts.py` I was able to fetch records mapping to lists properly in SQLite. This saves sequential `execute` calls on every record fetched, greatly reducing the time per API call.
**Action:** When finding `conn.execute` inside of loops querying relational items, batch query via joining or with the `IN` keyword.
