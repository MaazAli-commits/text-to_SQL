from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pandas as pd
from db import engine, run_query, load_csv_to_db
from security import is_dangerous
from utils import add_limit
from sql_generator import generate_sql, explain_sql, summarize_results
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

CURRENT_SCHEMA = "customers(id, name, city, spent)"

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    schema_info: str = ""


@app.get("/")
def root():
    return {"message": "Text to SQL API is running"}


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    global CURRENT_SCHEMA
    df = pd.read_csv(file.file)
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.lower()
    df.to_sql("uploaded_data", engine, if_exists="replace", index=False)
    CURRENT_SCHEMA = f"uploaded_data({', '.join(df.columns)})"
    return {
        "schema": CURRENT_SCHEMA,
        "columns": list(df.columns),
        "preview": df.head().to_dict(orient="records")
    }


@app.post("/query")
def query(request: QueryRequest):
    sql = generate_sql(request.question, CURRENT_SCHEMA, request.schema_info)

    if sql == "NOT_DB_QUESTION":
        return {"status": "not_db_question", "message": "I can only answer questions about the database."}

    if sql == "DANGEROUS_QUERY" or is_dangerous(sql):
        return {"status": "dangerous", "message": "Sorry, only SELECT queries are allowed."}

    sql = add_limit(sql)
    explanation = explain_sql(sql)

    try:
        rows, cols = run_query(sql)
        if rows:
            results = [dict(zip(cols, row)) for row in rows]
            summary = summarize_results(request.question, sql, results)
            return {
                "status": "success",
                "sql": sql,
                "explanation": explanation,
                "results": results,
                "summary": summary
            }
        else:
            return {"status": "empty", "message": "No matching records found."}
    except Exception as e:
        if "no such column" in str(e).lower():
            return {"status": "error", "message": "One or more columns do not exist."}
        return {"status": "error", "message": str(e)}