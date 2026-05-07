# Text-to-SQL LLM Application

A secure AI-powered Text-to-SQL application that converts natural language into SQL queries using LLMs.

Users can:

* Upload CSV files
* Ask questions in plain English
* Generate SQL automatically
* View explanations and summaries
* Download query results
* Interact through a Streamlit frontend + FastAPI backend

---

# Features

* Natural Language → SQL generation
* CSV upload support
* Dynamic schema detection
* Metadata-aware prompting
* SQL explanation in plain English
* Query result summarization
* SQL injection protection
* AST-based query validation using SQLGlot
* Query history and rerun support
* Download results as CSV
* Dockerized deployment
* FastAPI backend API
* Streamlit frontend UI

---

# Tech Stack

* Python
* Streamlit
* FastAPI
* SQLite
* SQLAlchemy
* Groq API
* SQLGlot
* Docker

---

# Project Architecture

```text
Frontend (Streamlit)
        ↓
FastAPI Backend
        ↓
LLM (Groq API)
        ↓
SQL Validation (SQLGlot AST)
        ↓
SQLite Database
```

---

# Security Features

This project includes multiple security protections:

* Only SELECT queries allowed
* Dangerous SQL blocked
* AST validation using SQLGlot
* Prompt injection filtering
* Column whitelist enforcement
* LIMIT added automatically
* Non-database questions rejected

---

# Example Workflow

1. Upload CSV file
2. Enter natural language question
3. LLM generates SQL query
4. Query validated using AST parsing
5. Query executed on SQLite database
6. Results displayed with explanation and summary

---

# Example Questions

```text
Show employees with salary above 100000

Which department has the highest average salary?

Show employees from Mumbai

List top performing employees
```

---

# Running Locally

## Clone repository

```bash
git clone https://github.com/MaazAli-commits/text-to_SQL.git
cd text-to_SQL
```

---

## Create virtual environment

```bash
python -m venv venv
```

Activate environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Add environment variables

Create `.env`

```env
GROQ_API_KEY=your_api_key_here
```

---

# Run Backend

```bash
uvicorn api:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

---

# Run Frontend

```bash
streamlit run app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

# Docker

Build image:

```bash
docker build -t text-to-sql .
```

Run container:

```bash
docker run -p 8501:8501 text-to-sql
```

---

# Future Improvements

* PostgreSQL support
* Multi-user session isolation
* Better semantic query understanding
* Query caching
* Authentication
* Charts and visual analytics
* Cloud deployment
* RAG-based schema retrieval

---

# Disclaimer

LLM-generated SQL and summaries may occasionally be logically incorrect.
Always verify results before making important decisions.

---

# Author

Maaz Ali
