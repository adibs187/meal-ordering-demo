"""Load sample restaurants and menu items into an empty database."""

from database import get_connection

RESTAURANTS = [
    ("המטבח של נועה", "ישראלי", 1, 1),
    ("פסטה בעיר", "איטלקי", 0, 1),
    ("גרין בול", "בריאות", 1, 1),
    ("ים וטעם", "דגים", 1, 1),
    ("מתוק בלב", "קינוחים", 1, 1),
]

MENU_ITEMS = [
    (1, "שקשוקה הבית", "עגבניות צלויות, ביצים וטחינה ירוקה", 52, 1),
    (2, "פסטה פטריות", "פטריות, שמנת, פרמזן וטימין", 64, 1),
    (3, "קערת קינואה", "קינואה, ירקות ועדשים", 57, 1),
    (4, "פילה סלמון", "סלמון צלוי וקרם כרובית", 88, 1),
    (5, "טארט לימון", "קרם לימון ומרנג", 44, 1),
]

with get_connection() as connection:
    cursor = connection.cursor()
    restaurant_count = cursor.execute(
        "SELECT COUNT(*) FROM dbo.Restaurant WITH (TABLOCKX, HOLDLOCK)"
    ).fetchval()
    menu_count = cursor.execute(
        "SELECT COUNT(*) FROM dbo.MenuItem WITH (TABLOCKX, HOLDLOCK)"
    ).fetchval()
    if restaurant_count or menu_count:
        raise SystemExit("Sample data can only be loaded when both tables are empty.")

    restaurant_ids = {}
    for sample_id, restaurant in enumerate(RESTAURANTS, start=1):
        restaurant_ids[sample_id] = cursor.execute(
            "INSERT INTO dbo.Restaurant (RestaurantName, Category, Kosher, IsOpen) "
            "OUTPUT INSERTED.RestaurantID VALUES (?, ?, ?, ?)",
            *restaurant,
        ).fetchval()
    cursor.executemany(
        "INSERT INTO MenuItem (RestaurantID, ItemName, Description, Price, InStock) VALUES (?, ?, ?, ?, ?)",
        [(restaurant_ids[sample_id], *item) for sample_id, *item in MENU_ITEMS],
    )
    restaurant_rows = cursor.execute(
        "SELECT TOP 5 RestaurantID, RestaurantName, Category, Kosher, IsOpen "
        "FROM Restaurant ORDER BY RestaurantID"
    ).fetchall()
    menu_rows = cursor.execute(
        "SELECT TOP 5 ItemID, ItemName, Price, InStock FROM MenuItem ORDER BY ItemID"
    ).fetchall()

    if len(restaurant_rows) != 5 or len(menu_rows) != 5:
        raise RuntimeError("Expected exactly five rows in Restaurant and five rows in MenuItem")

    print("Database connection succeeded.")
    print("Restaurant rows:")
    for row in restaurant_rows:
        print(row)
    print("MenuItem rows:")
    for row in menu_rows:
        print(row)
