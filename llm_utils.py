import os
import time
from google import genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_config(key, default=None):
    value = os.getenv(key)
    if value is None:
        try:
            value = st.secrets.get(key, default)
        except Exception:
            value = default
    return value

GEMINI_API_KEY = get_config("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-flash-lite-latest"


def generate_sql(user_question, schema_info):
    """
    Takes a plain-English question and the database schema,
    and asks Gemini to convert it into a SQL query.
    """

    prompt = f"""
You are an expert MySQL query generator.

Here is the database schema you must use:
{schema_info}

Rules:
- Only generate SELECT queries. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER statements.
- Only use the tables and columns listed above. Do not invent column names.
- Return ONLY the raw SQL query. No explanations, no markdown, no code fences like ```sql.
- Use proper JOINs when a question needs data from multiple tables.
- If the question cannot be answered using this schema, respond with exactly: INVALID_QUESTION

User question: "{user_question}"

SQL query:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    sql_query = response.text.strip()

    if sql_query.startswith("```"):
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    return sql_query


if __name__ == "__main__":
    import time
    from db_utils import get_schema_info, run_query

    print("Step 1: Getting schema...")
    schema = get_schema_info()
    print("Step 1 done.")

    print("Step 2: Calling Gemini API...")
    start = time.time()

    question = "What are the top 5 products by revenue?"
    sql = generate_sql(question, schema)

    elapsed = time.time() - start
    print(f"Step 2 done in {elapsed:.1f} seconds.")
    print("Generated SQL:")
    print(sql)

    print("\nStep 3: Running this SQL on the database...")
    result = run_query(sql)
    print(result)