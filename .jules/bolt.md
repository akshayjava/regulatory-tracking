## 2024-04-20 - [Optimize N+1 queries in SQLite fastAPI backend]
**Learning:** SQLite query loops in Python (N+1 queries) via DB fetchalls mapping models over REST endpoints can create significant bottlenecks even with an in-memory or highly optimized local file database. Using IN clauses for batch processing or `GROUP_CONCAT` in JOINs effectively solves this, turning O(N) operations into O(1) batched operations.
**Action:** Always batch related SQLite lookups using IN clauses or use JOINs rather than iterating and running separate subqueries per row.
## 2024-05-14 - [GROUP_CONCAT optimizations with multiple joins]
**Learning:** `GROUP_CONCAT` can be a powerful tool to batch 1-to-many relationships in a single SQLite query. However, be cautious of delimiter collisions (the default `,` is fine if names are strictly alphanumeric like `crypto`, `healthcare`, but may fail if values could contain commas). Also, splitting the string array in Python is fast.
**Action:** Use `GROUP_CONCAT` combined with `LEFT JOIN` + `GROUP BY` to optimize complex N+1 patterns where related sets of strings or simple attributes need to be fetched alongside parent records.
