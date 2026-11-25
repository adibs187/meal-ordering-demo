IF DB_ID(N'MealOrderingDemo') IS NULL
    EXEC(N'CREATE DATABASE MealOrderingDemo');
GO
USE MealOrderingDemo;
GO

IF OBJECT_ID(N'dbo.MenuItem', N'U') IS NOT NULL DROP TABLE dbo.MenuItem;
IF OBJECT_ID(N'dbo.Restaurant', N'U') IS NOT NULL DROP TABLE dbo.Restaurant;
GO

CREATE TABLE dbo.Restaurant (
    RestaurantID INT IDENTITY(1,1) PRIMARY KEY,
    RestaurantName NVARCHAR(100) NOT NULL,
    Category NVARCHAR(80) NOT NULL,
    Kosher BIT NOT NULL CONSTRAINT DF_Restaurant_Kosher DEFAULT 0,
    IsOpen BIT NOT NULL CONSTRAINT DF_Restaurant_IsOpen DEFAULT 1
);

CREATE TABLE dbo.MenuItem (
    ItemID INT IDENTITY(1,1) PRIMARY KEY,
    RestaurantID INT NOT NULL,
    ItemName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500) NULL,
    Price DECIMAL(10,2) NOT NULL,
    InStock BIT NOT NULL CONSTRAINT DF_MenuItem_InStock DEFAULT 1,
    UpdatedAt DATETIME2 NOT NULL CONSTRAINT DF_MenuItem_UpdatedAt DEFAULT SYSDATETIME(),
    CONSTRAINT FK_MenuItem_Restaurant FOREIGN KEY (RestaurantID)
        REFERENCES dbo.Restaurant(RestaurantID),
    CONSTRAINT CK_MenuItem_PositivePrice CHECK (Price > 0),
    CONSTRAINT UQ_MenuItem_Restaurant_Name UNIQUE (RestaurantID, ItemName)
);
GO
