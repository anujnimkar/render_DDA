{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww25400\viewh16000\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 -- Create the database\
CREATE DATABASE ECommerceDB;\
USE ECommerceDB;\
\
-- Create Products table\
CREATE TABLE Products (\
    ProductID INT PRIMARY KEY,\
    ProductName VARCHAR(100),\
    Category VARCHAR(50),\
    Price DECIMAL(10, 2),\
    StockQuantity INT\
);\
\
-- Create Customers table\
CREATE TABLE Customers (\
    CustomerID INT PRIMARY KEY,\
    FirstName VARCHAR(50),\
    LastName VARCHAR(50),\
    Email VARCHAR(100),\
    RegistrationDate DATE\
);\
\
-- Create Orders table\
CREATE TABLE Orders (\
    OrderID INT PRIMARY KEY,\
    CustomerID INT,\
    OrderDate DATE,\
    TotalAmount DECIMAL(10, 2),\
    Status VARCHAR(20),\
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)\
);\
\
-- Create OrderDetails table\
CREATE TABLE OrderDetails (\
    OrderDetailID INT PRIMARY KEY,\
    OrderID INT,\
    ProductID INT,\
    Quantity INT,\
    UnitPrice DECIMAL(10, 2),\
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),\
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)\
);\
\
-- Insert sample data into Products table\
INSERT INTO Products (ProductID, ProductName, Category, Price, StockQuantity) VALUES\
(1, 'Smartphone X', 'Electronics', 599.99, 100),\
(2, 'Laptop Pro', 'Electronics', 1299.99, 50),\
(3, 'Running Shoes', 'Sports', 89.99, 200),\
(4, 'Coffee Maker', 'Home Appliances', 79.99, 75),\
(5, 'Mystery Novel', 'Books', 14.99, 300);\
\
-- Insert sample data into Customers table\
INSERT INTO Customers (CustomerID, FirstName, LastName, Email, RegistrationDate) VALUES\
(1, 'John', 'Doe', 'john.doe@email.com', '2024-01-15'),\
(2, 'Jane', 'Smith', 'jane.smith@email.com', '2024-02-01'),\
(3, 'Bob', 'Johnson', 'bob.johnson@email.com', '2024-02-15'),\
(4, 'Alice', 'Williams', 'alice.williams@email.com', '2024-03-01'),\
(5, 'Charlie', 'Brown', 'charlie.brown@email.com', '2024-03-15');\
\
-- Insert sample data into Orders table\
INSERT INTO Orders (OrderID, CustomerID, OrderDate, TotalAmount, Status) VALUES\
(1, 1, '2025-01-20', 599.99, 'Completed'),\
(2, 2, '2025-01-25', 1389.98, 'Shipped'),\
(3, 3, '2025-02-01', 89.99, 'Processing'),\
(4, 4, '2025-02-05', 94.98, 'Completed'),\
(5, 5, '2025-02-10', 1299.99, 'Shipped');\
\
-- Insert sample data into OrderDetails table\
INSERT INTO OrderDetails (OrderDetailID, OrderID, ProductID, Quantity, UnitPrice) VALUES\
(1, 1, 1, 1, 599.99),\
(2, 2, 2, 1, 1299.99),\
(3, 2, 3, 1, 89.99),\
(4, 3, 3, 1, 89.99),\
(5, 4, 4, 1, 79.99),\
(6, 4, 5, 1, 14.99),\
(7, 5, 2, 1, 1299.99);\
\
-- Select all products with their categories and prices\
SELECT ProductID, ProductName, Category, Price\
FROM Products;\
\
-- Select all customers and their registration dates\
SELECT CustomerID, FirstName, LastName, Email, RegistrationDate\
FROM Customers;\
\
-- Select all orders with customer information\
SELECT o.OrderID, c.FirstName, c.LastName, o.OrderDate, o.TotalAmount, o.Status\
FROM Orders o\
JOIN Customers c ON o.CustomerID = c.CustomerID;\
\
-- Select order details with product information\
SELECT od.OrderID, p.ProductName, od.Quantity, od.UnitPrice\
FROM OrderDetails od\
JOIN Products p ON od.ProductID = p.ProductID;\
\
-- Calculate total revenue by product category\
SELECT p.Category, SUM(od.Quantity * od.UnitPrice) AS TotalRevenue\
FROM OrderDetails od\
JOIN Products p ON od.ProductID = p.ProductID\
GROUP BY p.Category;\
\
-- Find top 3 bestselling products\
SELECT p.ProductID, p.ProductName, SUM(od.Quantity) AS TotalSold\
FROM OrderDetails od\
JOIN Products p ON od.ProductID = p.ProductID\
GROUP BY p.ProductID, p.ProductName\
ORDER BY TotalSold DESC\
LIMIT 3;\
\
-- Calculate average order value\
SELECT AVG(TotalAmount) AS AverageOrderValue\
FROM Orders;\
\
-- Find customers who have made more than one order\
SELECT c.CustomerID, c.FirstName, c.LastName, COUNT(o.OrderID) AS OrderCount\
FROM Customers c\
JOIN Orders o ON c.CustomerID = o.CustomerID\
GROUP BY c.CustomerID, c.FirstName, c.LastName\
HAVING OrderCount > 1;\
\
-- Calculate the total revenue for each month\
SELECT DATE_FORMAT(OrderDate, '%Y-%m') AS Month, SUM(TotalAmount) AS MonthlyRevenue\
FROM Orders\
GROUP BY Month\
ORDER BY Month;\
\
-- Find products with low stock (less than 100 units)\
SELECT ProductID, ProductName, StockQuantity\
FROM Products\
WHERE StockQuantity < 100;\
\
-- Calculate the average time between customer registration and first order\
SELECT AVG(DATEDIFF(o.OrderDate, c.RegistrationDate)) AS AvgDaysTillFirstOrder\
FROM Customers c\
JOIN Orders o ON c.CustomerID = o.CustomerID\
WHERE o.OrderID = (\
    SELECT MIN(OrderID)\
    FROM Orders\
    WHERE CustomerID = c.CustomerID\
);\
\
-- Find the most popular product category by order quantity\
SELECT p.Category, SUM(od.Quantity) AS TotalQuantity\
FROM OrderDetails od\
JOIN Products p ON od.ProductID = p.ProductID\
GROUP BY p.Category\
ORDER BY TotalQuantity DESC\
LIMIT 1; \
\
-- Calculate the percentage of completed orders\
SELECT \
    (COUNT(CASE WHEN Status = 'Completed' THEN 1 END) * 100.0 / COUNT(*)) AS CompletedOrderPercentage\
FROM Orders;\
\
-- Find customers who have purchased a specific product (e.g., 'Laptop Pro')\
SELECT DISTINCT c.CustomerID, c.FirstName, c.LastName\
FROM Customers c\
JOIN Orders o ON c.CustomerID = o.CustomerID\
JOIN OrderDetails od ON o.OrderID = od.OrderID\
JOIN Products p ON od.ProductID = p.ProductID\
WHERE p.ProductName = 'Laptop Pro';\
\
-- Calculate the average number of products per order\
SELECT AVG(ProductCount) AS AvgProductsPerOrder\
FROM (\
    SELECT OrderID, COUNT(ProductID) AS ProductCount\
    FROM OrderDetails\
    GROUP BY OrderID\
) AS OrderProductCounts;\
\
-- Find the total revenue generated by each customer\
SELECT c.CustomerID, c.FirstName, c.LastName, SUM(o.TotalAmount) AS TotalRevenue\
FROM Customers c\
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID\
GROUP BY c.CustomerID, c.FirstName, c.LastName\
ORDER BY TotalRevenue DESC;\
\
-- Create a final summary table\
CREATE TABLE OrderSummary AS\
SELECT \
    o.OrderID,\
    c.CustomerID,\
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,\
    o.OrderDate,\
    o.TotalAmount,\
    o.Status,\
    COUNT(od.ProductID) AS TotalProducts,\
    GROUP_CONCAT(p.ProductName SEPARATOR ', ') AS ProductsList\
FROM Orders o\
JOIN Customers c ON o.CustomerID = c.CustomerID\
JOIN OrderDetails od ON o.OrderID = od.OrderID\
JOIN Products p ON od.ProductID = p.ProductID\
GROUP BY o.OrderID, c.CustomerID, CustomerName, o.OrderDate, o.TotalAmount, o.Status;\
\
-- Select data from the final summary table\
SELECT * FROM OrderSummary;\
\
}