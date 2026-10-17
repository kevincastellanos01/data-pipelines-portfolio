# SQL analytics

Queries against the [Northwind](https://github.com/jpwhite3/northwind-SQLite3) sample database in SQLite. The tables used here are `Customers`, `Orders`, and `Products`.

The script answers nine questions a reporting layer usually starts with: who the customers are, where they are, which orders they placed, and which products need attention.

## Queries

| # | Question | Technique |
| --- | --- | --- |
| 1 | Which countries have customers? | `DISTINCT`, `ORDER BY` |
| 2 | How many countries is that? | `COUNT(DISTINCT ...)` |
| 3 | How many orders did customer `FRANK` place? | Filtered aggregate |
| 4 | Which active products are out of stock? | Combined predicates |
| 5 | Which active products are short, or over-ordered? | `OR` inside a filtered set |
| 6 | Who ordered in December? | `strftime` on `OrderDate` |
| 7 | Who are the North American contacts? | `IN` |
| 8 | Which companies have no fax? | `IS NULL` |
| 9 | What are the five most expensive products? | Sort, `LIMIT`, formatted price |

Query 9 labels the rounded price as `Price` and prefixes it with `$`.

## Run

Open `northwind_queries.sql` in DB Browser for SQLite, DBeaver, or the `sqlite3` shell, against a Northwind SQLite file.

```bash
sqlite3 northwind.db < northwind_queries.sql
```
