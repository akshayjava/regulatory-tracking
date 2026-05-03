## 2024-05-24 - SQLite N+1 Queries
**Learning:** Using `GROUP_CONCAT` coupled with a `LEFT JOIN` and `GROUP BY` is an extremely effective way to avoid N+1 query patterns in SQLite while keeping the query logic relatively simple.
**Action:** When fetching relational datasets (like regulations and their associated verticals), look for opportunities to bundle the child objects into a concatenated string field using `GROUP_CONCAT`, then split the string in the application layer. This eliminates the need for separate subqueries per row.
