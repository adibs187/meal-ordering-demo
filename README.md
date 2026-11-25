# Meal Ordering Demo

A restaurant menu management module built for an Information Systems Analysis and Design course. It demonstrates the workflow from a Hebrew right-to-left web interface, through a REST API, to a relational database.

## What the demo does

| Use case | API route |
| --- | --- |
| UC024 · Add a menu item | `POST /api/menu-items` |
| UC025 · Edit a price and description | `PUT /api/menu-items/{item_id}` |
| UC026 · Toggle item availability | `PATCH /api/menu-items/{item_id}/stock` |

The browser UI uses HTML, CSS and JavaScript. FastAPI serves the interface and API. The backend uses pyodbc to read and write the `Restaurant` and `MenuItem` tables in Microsoft SQL Server.

## Run locally

On Windows, use Python 3.12, SQL Server and Microsoft ODBC Driver 18 for SQL Server. Run [the schema script](sql/01_create_database.sql) against a fresh demo database using SQL Server Management Studio. Running that script again drops and recreates the demo tables.

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and match `DB_SERVER` to the SQL Server instance. The template defaults to Windows authentication. Then seed the empty tables and start the server:

```powershell
.\.venv312\Scripts\python.exe seed_demo_data.py
.\.venv312\Scripts\python.exe -m uvicorn main:app --reload
```

Open the [demo](http://127.0.0.1:8000) or the [interactive API docs](http://127.0.0.1:8000/docs). Try updating a menu item and run [the verification query](sql/02_verify_changes.sql) to see the stored result.

For the full setup guide in Hebrew, see [הוראות הפעלה](docs/setup-he.md).
