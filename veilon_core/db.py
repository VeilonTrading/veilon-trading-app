import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

db = st.secrets["database"]
host = db["DB_HOST"]
port = db["DB_PORT"]
dbname = db["DB_NAME"]
user = db["DB_USER"]
password = db["DB_PASSWORD"]

def execute_query(query, params=None, fetch_results=True):
    """
    Executes a SQL query and optionally fetches results.

    Returns:
      - If fetch_results=True: always returns a list (possibly empty)
      - If fetch_results=False: returns None on success (raises/prints on error)
    """
    try:
        with psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password,
        ) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)

                if not fetch_results:
                    # Using "with conn" commits automatically on normal exit,
                    # but explicit commit is fine and clear.
                    conn.commit()
                    return None

                rows = cursor.fetchall()
                return rows if rows is not None else []

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        # Critical change: never return None for SELECT-style calls
        return [] if fetch_results else None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [] if fetch_results else None