USE MealOrderingDemo;
GO
SELECT RestaurantID, RestaurantName, Category, Kosher, IsOpen
FROM dbo.Restaurant ORDER BY RestaurantID;

SELECT ItemID, RestaurantID, ItemName, Description, Price, InStock, UpdatedAt
FROM dbo.MenuItem ORDER BY UpdatedAt DESC;
GO
