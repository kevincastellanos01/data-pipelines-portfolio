# SQL analytics

These queries run on the [Northwind](https://github.com/jpwhite3/northwind-SQLite3) sample database in SQLite. I used `Customers`, `Orders`, and `Products` because the useful questions sit on those three tables: where customers are, who ordered, and which products cannot be sold.

## What I kept in, and what I left out

Active products are `Discontinued = 0`. A stock report that includes discontinued items flags products the catalog already retired, so queries 4 and 5 apply that filter before they look at `UnitsInStock` and `UnitsOnOrder`.

Query 5 treats two different problems as one list: nothing left to ship, or more units already on order than units on hand. Both need a purchasing look. They stay in one result so the list is the action queue, not two reports that have to be merged later.

December orders use `strftime('%m', OrderDate)`. In this SQLite file `OrderDate` is text in ISO form, and the month is the part the question cares about. The customer id is `DISTINCT` because one customer can place several orders in the same month.

The price column in query 9 is a display value: `printf('$%.0f', UnitPrice)` rounds to the nearest dollar and adds the currency sign. The sort stays on `UnitPrice`, so two prices that round to the same dollar keep their real order.

Missing fax numbers use `IS NULL`. An empty string is a different fact, and this table stores the absence as null.

## Queries

| # | Question |
| --- | --- |
| 1 | Which countries have customers? |
| 2 | How many countries is that? |
| 3 | How many orders did customer `FRANK` place? |
| 4 | Which active products are out of stock? |
| 5 | Which active products are short, or have more units on order than in stock? |
| 6 | Who ordered in December? |
| 7 | Who are the North American contacts? |
| 8 | Which companies have no fax number? |
| 9 | What are the five most expensive products, with a rounded display price? |

## Run

```bash
sqlite3 northwind.db < northwind_queries.sql
```

The same file opens in DB Browser for SQLite or DBeaver.
