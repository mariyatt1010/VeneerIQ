import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sql_validator import validate_sql, enforce_row_limit

# Load secret values (host, password, etc.) from the .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        ssl_disabled=False
    )
    return connection


def get_engine():
    engine = create_engine(
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_disabled=False"
    )
    return engine


def run_query(sql_query):
    """
    Takes a SQL query as text, runs it on the database,
    and returns the results as a pandas DataFrame (a clean table format).
    """
    engine = get_engine()
    result_df = pd.read_sql(sql_query, engine)
    return result_df


def run_query_safely(sql_query):
    """
    Flow: Generated SQL -> SQL Validator -> Row Limit -> MySQL
    Validates the query, enforces a max row limit, then executes it.
    Raises ValueError if the query is blocked.
    """
    validate_sql(sql_query)
    safe_query = enforce_row_limit(sql_query)
    return run_query(safe_query)


def get_schema_info():
    """
    Returns a text description of our database structure (table names, columns,
    and example values for text columns) so the AI knows exact wording to use.
    """
    connection = get_connection()
    cursor = connection.cursor()

    schema_text = ""
    tables = ["customers", "products", "sales"]

    # Columns where showing real distinct values helps the AI match text exactly
    text_columns_to_sample = {
        "customers": ["customer_type", "city"],
        "products": ["category"],
    }

    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        schema_text += f"\nTable: {table}\n"
        for col in columns:
            schema_text += f"  - {col[0]} ({col[1]})\n"

        # Add real example values for known text columns in this table
        if table in text_columns_to_sample:
            for col_name in text_columns_to_sample[table]:
                cursor.execute(f"SELECT DISTINCT {col_name} FROM {table}")
                values = [row[0] for row in cursor.fetchall()]
                schema_text += f"    Example values for {col_name}: {values}\n"

    cursor.close()
    connection.close()
    return schema_text


# This block only runs if you execute this file directly (for testing)
if __name__ == "__main__":
    print("Testing database connection...")
    print(get_schema_info())

    print("\nTesting a sample query...")
    df = run_query("SELECT * FROM customers LIMIT 3;")
    print(df)

    print("\nTesting the safety layer...")
    from sql_validator import is_safe_query
    test_queries = [
        "SELECT * FROM sales",
        "DROP TABLE sales",
        "SELECT * FROM sales; DROP TABLE sales;",
        "SELECT * FROM sales WHERE customer_id = 1; DELETE FROM sales",
    ]
    for q in test_queries:
        print(f"{q!r} -> {is_safe_query(q)}")