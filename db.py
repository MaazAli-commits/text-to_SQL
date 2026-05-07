import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///sample.db")

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            spent REAL
        )
    """))
    conn.execute(text("""
        INSERT OR IGNORE INTO customers VALUES
        (1, 'Raj', 'Mumbai', 8000),
        (2, 'Priya', 'Bangalore', 3000),
        (3, 'Arjun', 'Chennai', 12000),
        (4, 'Sneha', 'Delhi', 4500),
        (5, 'Karan', 'Bangalore', 9500)
    """))
    conn.commit()

SCHEMA = "customers(id, name, city, spent)"
VALID_COLUMNS = {"id", "name", "city", "spent"}

def load_csv_to_db(uploaded_file):
    df = pd.read_csv(uploaded_file)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.lower()
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    df.to_sql("uploaded_data", engine, if_exists="replace", index=False)
    return df

def run_query(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        cols = result.keys()
        return rows, cols