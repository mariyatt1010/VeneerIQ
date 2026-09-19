import streamlit as st
import pandas as pd
from db_utils import get_schema_info, run_query, run_query_safely
from llm_utils import generate_sql
from visualization_utils import render_visualization
from summary_utils import generate_business_summary

st.set_page_config(page_title="AI-Powered BI Dashboard", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Fraunces', serif !important;
        color: #4A3728 !important;
    }

    .stApp {
        background-color: #FBF7F0;
    }

    [data-testid="stMetric"] {
        background-color: #F1E9DD;
        border: 1px solid #D8C9B4;
        border-radius: 12px;
        padding: 16px 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #8A6F52 !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #4A3728 !important;
    }

    .stTextInput input {
        border: 1.5px solid #C9B79C !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
    }

    .stButton button {
        background-color: #A9714B !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }

    [data-testid="stExpander"] {
        background-color: #F5EFE4;
        border-radius: 10px;
        border: 1px solid #E0D3BC;
    }

    .stAlert {
        border-radius: 10px !important;
    }

    hr {
        border-color: #E0D3BC !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(""" <div style="text-align: center; padding: 1rem 0;"> <h1 style="margin-bottom: 0;">Veneer Insights</h1> <p style="color: #8B6F47; font-size: 1.1rem; margin-top: 0.25rem;"> Turn your business data into actionable insights </p> </div> """, unsafe_allow_html=True)

# ---------- KPI CARDS ----------
@st.cache_data(ttl=60)
def get_kpis():
    total_revenue = run_query("SELECT SUM(total_amount) AS val FROM sales")["val"][0]
    total_orders = run_query("SELECT COUNT(*) AS val FROM sales")["val"][0]
    total_customers = run_query("SELECT COUNT(*) AS val FROM customers")["val"][0]
    top_customer = run_query("""
        SELECT c.customer_name, SUM(s.total_amount) AS revenue
        FROM sales s JOIN customers c ON s.customer_id = c.customer_id
        GROUP BY c.customer_name ORDER BY revenue DESC LIMIT 1
    """)
    top_customer_name = top_customer["customer_name"][0]
    return total_revenue, total_orders, total_customers, top_customer_name


total_revenue, total_orders, total_customers, top_customer_name = get_kpis()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders}")
col3.metric("Total Customers", f"{total_customers}")
col4.metric("Top Customer", top_customer_name, help=top_customer_name)

st.divider()

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of dicts describing each Q&A turn

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def render_answer(entry):
    """Renders one assistant turn: SQL, insight, table, CSV download, chart."""
    with st.expander("🔍 View Generated SQL"):
        st.code(entry["sql"], language="sql")
    st.info(f"💡 {entry['summary']}")
    st.dataframe(entry["result"], width="stretch")

    csv_bytes = entry["result"].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_bytes,
        file_name="query_result.csv",
        mime="text/csv",
        key=f"csv_download_{entry['id']}",
    )

    render_visualization(entry["question"], entry["result"])


def handle_question(question):
    """Runs the full pipeline for a question and stores the result in history."""
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            schema = get_schema_info()
            sql_query = generate_sql(question, schema)

        if sql_query.strip() == "INVALID_QUESTION":
            st.warning("Sorry, I couldn't turn that into a valid query. Try rephrasing your question.")
            st.session_state.messages.append({
                "id": len(st.session_state.messages),
                "question": question,
                "kind": "invalid",
            })
            return

        try:
            result_df = run_query_safely(sql_query)
            with st.spinner("Generating insight..."):
                summary_text = generate_business_summary(question, result_df)

            entry = {
                "id": len(st.session_state.messages),
                "question": question,
                "sql": sql_query,
                "result": result_df,
                "summary": summary_text,
                "kind": "answer",
            }
            render_answer(entry)
            st.session_state.messages.append(entry)

        except ValueError as e:
            st.error(f"🚫 {e}")
            st.session_state.messages.append({
                "id": len(st.session_state.messages),
                "question": question,
                "kind": "error",
                "message": f"🚫 {e}",
            })
        except Exception as e:
            st.error(f"Something went wrong running this query: {e}")
            st.session_state.messages.append({
                "id": len(st.session_state.messages),
                "question": question,
                "kind": "error",
                "message": f"Something went wrong running this query: {e}",
            })


# ---------- SUGGESTED QUESTION CHIPS ----------
st.write("**Try asking:**")
suggested_questions = [
    "Top 5 products by revenue",
    "Total sales by city",
    "Which customer type buys the most?",
    "Monthly revenue trend",
]
chip_cols = st.columns(len(suggested_questions))
for col, question_text in zip(chip_cols, suggested_questions):
    if col.button(question_text, width="stretch"):
        st.session_state.pending_question = question_text

st.divider()

# ---------- REPLAY EXISTING CONVERSATION ----------
for entry in st.session_state.messages:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        if entry["kind"] == "invalid":
            st.warning("Sorry, I couldn't turn that into a valid query. Try rephrasing your question.")
        elif entry["kind"] == "error":
            st.error(entry["message"])
        else:
            render_answer(entry)

# ---------- CHAT INPUT ----------
typed_question = st.chat_input("Ask a question about your business data...")

# A clicked suggestion chip takes priority if present this run
active_question = st.session_state.pending_question or typed_question
st.session_state.pending_question = None  # clear so it only fires once

if active_question:
    with st.chat_message("user"):
        st.write(active_question)
    handle_question(active_question)
