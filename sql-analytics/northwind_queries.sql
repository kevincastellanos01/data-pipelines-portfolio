-- Northwind sample database (SQLite).
-- Customers, Orders, and Products.

-- 1. Distinct countries where customers are located, sorted alphabetically.
SELECT DISTINCT Country
FROM Customers
ORDER BY Country;

-- 2. Number of distinct countries where customers are located.
SELECT COUNT(DISTINCT Country) AS country_count
FROM Customers;

-- 3. Number of orders placed by customer FRANK.
SELECT COUNT(*) AS order_count
FROM Orders
WHERE CustomerID = 'FRANK';

-- 4. Products that are still sold and currently out of stock.
SELECT ProductID, ProductName
FROM Products
WHERE Discontinued = 0
  AND UnitsInStock = 0;

-- 5. Active products that are out of stock, or have more units on order than in stock.
SELECT ProductID, ProductName, UnitsInStock, UnitsOnOrder
FROM Products
WHERE Discontinued = 0
  AND (UnitsInStock = 0 OR UnitsOnOrder > UnitsInStock);

-- 6. Distinct customers who placed an order in December.
SELECT DISTINCT CustomerID
FROM Orders
WHERE strftime('%m', OrderDate) = '12';

-- 7. Company, contact, title, and phone for North American customers.
SELECT CompanyName, ContactName, ContactTitle, Phone
FROM Customers
WHERE Country IN ('USA', 'Canada', 'Mexico');

-- 8. Companies with no fax number.
SELECT CompanyName
FROM Customers
WHERE Fax IS NULL;

-- 9. Five most expensive products. Price is rounded to the nearest dollar.
SELECT
    ProductID,
    ProductName,
    printf('$%.0f', UnitPrice) AS Price
FROM Products
ORDER BY UnitPrice DESC
LIMIT 5;
