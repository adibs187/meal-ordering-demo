from decimal import Decimal
from pathlib import Path

import pyodbc
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from database import get_connection

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="מערכת הזמנת ארוחות - ניהול תפריט", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class MenuItemInput(BaseModel):
    restaurant_id: int = Field(gt=0)
    item_name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0, le=Decimal("9999.99"))
    in_stock: bool = True

    @field_validator("item_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("שם המנה חייב להכיל לפחות שני תווים")
        return value


class MenuItemUpdate(BaseModel):
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0, le=Decimal("9999.99"))


class StockInput(BaseModel):
    in_stock: bool


def row_to_dict(row) -> dict:
    return {
        "item_id": row.ItemID,
        "restaurant_id": row.RestaurantID,
        "item_name": row.ItemName,
        "description": row.Description or "",
        "price": float(row.Price),
        "in_stock": bool(row.InStock),
        "updated_at": row.UpdatedAt.isoformat(),
    }


def translate_db_error(error: pyodbc.Error) -> HTTPException:
    message = str(error)
    if "UQ_MenuItem_Restaurant_Name" in message or "2601" in message or "2627" in message:
        return HTTPException(status_code=409, detail="כבר קיימת מנה בשם הזה במסעדה")
    return HTTPException(status_code=503, detail="לא ניתן להתחבר למסד הנתונים")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/restaurants")
def restaurants():
    try:
        with get_connection() as connection:
            rows = connection.cursor().execute(
                "SELECT RestaurantID, RestaurantName FROM Restaurant ORDER BY RestaurantName"
            ).fetchall()
            return [{"restaurant_id": r.RestaurantID, "restaurant_name": r.RestaurantName} for r in rows]
    except pyodbc.Error as error:
        raise translate_db_error(error) from error


@app.get("/api/menu-items")
def list_menu_items(restaurant_id: int = Query(gt=0)):
    try:
        with get_connection() as connection:
            rows = connection.cursor().execute(
                """
                SELECT ItemID, RestaurantID, ItemName, Description, Price, InStock, UpdatedAt
                FROM MenuItem WHERE RestaurantID = ? ORDER BY UpdatedAt DESC, ItemID DESC
                """,
                restaurant_id,
            ).fetchall()
            return [row_to_dict(row) for row in rows]
    except pyodbc.Error as error:
        raise translate_db_error(error) from error


@app.post("/api/menu-items", status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemInput):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if not cursor.execute(
                "SELECT 1 FROM Restaurant WHERE RestaurantID = ?", payload.restaurant_id
            ).fetchone():
                raise HTTPException(status_code=404, detail="המסעדה לא נמצאה")
            row = cursor.execute(
                """
                INSERT INTO MenuItem (RestaurantID, ItemName, Description, Price, InStock)
                OUTPUT INSERTED.ItemID, INSERTED.RestaurantID, INSERTED.ItemName,
                       INSERTED.Description, INSERTED.Price, INSERTED.InStock, INSERTED.UpdatedAt
                VALUES (?, ?, ?, ?, ?)
                """,
                payload.restaurant_id,
                payload.item_name,
                payload.description.strip(),
                payload.price,
                payload.in_stock,
            ).fetchone()
            return row_to_dict(row)
    except HTTPException:
        raise
    except pyodbc.Error as error:
        raise translate_db_error(error) from error


@app.put("/api/menu-items/{item_id}")
def update_menu_item(item_id: int, payload: MenuItemUpdate):
    try:
        with get_connection() as connection:
            row = connection.cursor().execute(
                """
                UPDATE MenuItem
                SET Description=?, Price=?, UpdatedAt=SYSDATETIME()
                OUTPUT INSERTED.ItemID, INSERTED.RestaurantID, INSERTED.ItemName,
                       INSERTED.Description, INSERTED.Price, INSERTED.InStock, INSERTED.UpdatedAt
                WHERE ItemID=?
                """,
                payload.description.strip(),
                payload.price,
                item_id,
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="המנה לא נמצאה")
            return row_to_dict(row)
    except HTTPException:
        raise
    except pyodbc.Error as error:
        raise translate_db_error(error) from error


@app.patch("/api/menu-items/{item_id}/stock")
def update_stock(item_id: int, payload: StockInput):
    try:
        with get_connection() as connection:
            row = connection.cursor().execute(
                """
                UPDATE MenuItem SET InStock=?, UpdatedAt=SYSDATETIME()
                OUTPUT INSERTED.ItemID, INSERTED.RestaurantID, INSERTED.ItemName,
                       INSERTED.Description, INSERTED.Price, INSERTED.InStock, INSERTED.UpdatedAt
                WHERE ItemID=?
                """,
                payload.in_stock,
                item_id,
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="המנה לא נמצאה")
            return row_to_dict(row)
    except HTTPException:
        raise
    except pyodbc.Error as error:
        raise translate_db_error(error) from error
