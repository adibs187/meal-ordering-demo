# Meal Ordering Demo

## Overview

A restaurant menu management app backed by Microsoft SQL Server. It demonstrates how changes made in a browser are validated by a REST API and saved to a relational database.

## Features

- Select a restaurant and view its menu.
- Add menu items and edit their prices and descriptions.
- Mark items as out of stock or available again.

## Tech Stack

Python 3.12, FastAPI, Uvicorn, pyodbc, Microsoft SQL Server, HTML, CSS, and JavaScript.

## Getting Started

1. Install Python 3.12, Microsoft SQL Server, SQL Server Management Studio, and Microsoft ODBC Driver 18 for SQL Server.
2. Run [the schema script](sql/01_create_database.sql) in SQL Server Management Studio for a fresh demo setup. The script recreates the demo tables and clears their existing contents.
3. From the repository root, run the following in PowerShell.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Set `DB_SERVER` in `.env` to your SQL Server instance. The example uses Windows authentication.
5. Seed the empty demo tables and start the app.

```powershell
.\.venv\Scripts\python.exe seed_demo_data.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open the [app](http://127.0.0.1:8000) or the [interactive API documentation](http://127.0.0.1:8000/docs). Run [the verification query](sql/02_verify_changes.sql) to inspect saved changes.

## Repository Structure

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI routes and app entry point |
| `database.py` | SQL Server connection configuration |
| `static/` | Browser interface |
| `sql/` | Database schema and verification query |
| `seed_demo_data.py` | Sample restaurants and menu items |
| `tests/` | Project structure and application contract checks |
