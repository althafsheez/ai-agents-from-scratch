import os
from os import path
from pathlib import Path

import pandas as pd
import duckdb
from langfuse.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    timeout=60,
)

MODEL = "gemini-3.5-flash-lite"

WORKSPACE = Path(__file__).resolve().parents[1] / "workspace"

SQL_GENERATION_PROMPT = """
Generate an SQL query based on a prompt.
Do not reply with anything besides the SQL query.

The prompt is: {prompt}

The available columns are: {columns}
The table name is: {table_name}

Only generate a SELECT query.
"""


def generate_sql_query(
    prompt: str,
    columns: list,
    table_name: str
) -> str:
    """Generate an SQL query based on a prompt."""

    formatted_prompt = SQL_GENERATION_PROMPT.format(
        prompt=prompt,
        columns=columns,
        table_name=table_name
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
    )

    return response.choices[0].message.content or ""

def lookup_data(prompt: str, filepath: str) -> str:
    """Look up information from a CSV or Parquet dataset using SQL."""

    try:
        table_name = "dataset"

        # Step 1: Load dataset
        path = (WORKSPACE / filepath).resolve()

        if not path.is_relative_to(WORKSPACE.resolve()):
            raise PermissionError("Access outside workspace denied")

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError("Unsupported file format")

        # Create DuckDB connection
        con = duckdb.connect(":memory:")

        try:
            con.register(table_name, df)

            # Step 2: Generate SQL
            sql_query = generate_sql_query(
                prompt,
                df.columns.tolist(),
                table_name
            )

            sql_query = sql_query.strip()
            sql_query = sql_query.replace("```sql", "")
            sql_query = sql_query.replace("```", "").strip()

            # Step 3: Execute SQL
            result = con.sql(sql_query).df()

            return result.to_string(index=False)

        finally:
            con.close()

    except Exception as e:
        return f"Error accessing data: {str(e)}"