import os
from contextlib import contextmanager

import pyodbc
from dotenv import load_dotenv

load_dotenv()


def connection_string(database: str | None = None) -> str:
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    server = os.getenv("DB_SERVER", "localhost")
    db_name = database or os.getenv("DB_NAME", "MealOrderingDemo")
    trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() == "yes"
    trust_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={db_name}",
        f"TrustServerCertificate={trust_cert}",
    ]
    if trusted:
        parts.append("Trusted_Connection=yes")
    else:
        parts.extend(
            [
                f"UID={os.environ['DB_USER']}",
                f"PWD={os.environ['DB_PASSWORD']}",
            ]
        )
    return ";".join(parts)


@contextmanager
def get_connection():
    connection = pyodbc.connect(connection_string(), timeout=8)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
