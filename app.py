import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# session state init
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "rerun_query" not in st.session_state:
    st.session_state.rerun_query = ""
if "SCHEMA" not in st.session_state:
    st.session_state.SCHEMA = "customers(id, name, city, spent)"
if "SCHEMA_INFO" not in st.session_state:
    st.session_state.SCHEMA_INFO = ""
if "df" not in st.session_state:
    st.session_state.df = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# sidebar
with st.sidebar:
    st.header("📋 Schema")
    st.code(st.session_state.SCHEMA, language="sql")
    st.divider()
    st.header("🕘 Query History")
    if not st.session_state.query_history:
        st.caption("No queries yet. Ask something!")
    else:
        for i, entry in enumerate(reversed(st.session_state.query_history)):
            idx = len(st.session_state.query_history) - 1 - i
            with st.expander(f"[{entry['time']}] {entry['question'][:40]}…" if len(entry['question']) > 40 else f"[{entry['time']}] {entry['question']}"):
                st.code(entry["sql"], language="sql")
                st.caption(f"Returned {entry['row_count']} row(s)")
                if st.button("Re-run this", key=f"rerun_{idx}"):
                    st.session_state.rerun_query = entry["question"]
                    st.rerun()
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()

# main UI
st.title("Text to SQL")
st.write("Ask anything about your database")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file and uploaded_file.name != st.session_state.last_uploaded_file:
    st.session_state.last_uploaded_file = uploaded_file.name
    response = requests.post(
        f"{API_URL}/upload-csv",
        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
        timeout = 60
    )
    data = response.json()
    st.session_state.SCHEMA = data["schema"]
    st.session_state.df = pd.read_csv(uploaded_file)
    df = st.session_state.df
    st.success("CSV uploaded successfully!")
    st.dataframe(df.head())
    st.subheader("Optional Column Metadata")
    metadata = {}
    for col in df.columns:
        metadata[col] = st.text_input(
            f"Description for '{col}'",
            placeholder=f"Explain what '{col}' means"
        )
    st.session_state.SCHEMA_INFO = "\n".join(
        [f"{col}: {metadata[col]}" for col in df.columns if metadata[col].strip() != ""]
    )

elif st.session_state.df is not None:
    df = st.session_state.df
    st.dataframe(df.head())
    st.subheader("Optional Column Metadata")
    metadata = {}
    for col in df.columns:
        metadata[col] = st.text_input(
            f"Description for '{col}'",
            placeholder=f"Explain what '{col}' means"
        )
    st.session_state.SCHEMA_INFO = "\n".join(
        [f"{col}: {metadata[col]}" for col in df.columns if metadata[col].strip() != ""]
    )

# handle rerun
rerun_q = st.session_state.rerun_query
if rerun_q:
    st.session_state.rerun_query = ""

question = st.text_input("Your question:")
active_question = rerun_q if rerun_q else question

if active_question:
    try:
        with st.spinner("Generating SQL and analyzing results..."):
            response = requests.post(f"{API_URL}/query", json={
                "question": active_question,
                "schema_info": st.session_state.SCHEMA_INFO
            }, timeout=60)
        data = response.json()

        if data["status"] == "not_db_question":
            st.warning(data["message"])
        elif data["status"] == "dangerous":
            st.error(data["message"])
        elif data["status"] == "error":
            st.error(data["message"])
        elif data["status"] == "empty":
            st.info(data["message"])
        elif data["status"] == "success":
            st.code(data["sql"], language="sql")

            st.session_state.query_history.append({
                "question": active_question,
                "sql": data["sql"],
                "row_count": len(data["results"]),
                "time": datetime.now().strftime("%H:%M:%S"),
            })

            st.subheader("What this query does")
            st.info(data["explanation"])

            st.subheader("Results")
            results_df = pd.DataFrame(data["results"])

            if not results_df.empty:
                st.dataframe(results_df)
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )
                st.subheader("What we found")
                st.success(data["summary"])
            else:
                st.info("No matching records found.")

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure the API server is running.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")