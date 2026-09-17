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

st.title("AI-Powered BI Dashboard")
st.caption("Ask a business question in plain English — powered by Gemini + MySQL")

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

# ---------- QUERY HISTORY ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- CHAT INPUT ----------
user_question = st.text_input(
    "Ask a question about your business data:",
    placeholder="e.g. What are the top 5 products by revenue?"
)

if user_question:
    with st.spinner("Thinking..."):
        schema = get_schema_info()
        sql_query = generate_sql(user_question, schema)

    if sql_query.strip() == "INVALID_QUESTION":
        st.warning("Sorry, I couldn't turn that into a valid query. Try rephrasing your question.")
    else:
        try:
            # Flow: Generated SQL -> SQL Validator -> MySQL
            result_df = run_query_safely(sql_query)

            with st.expander("🔍 View Generated SQL"):
                st.code(sql_query, language="sql")

            with st.spinner("Generating insight..."):
                summary_text = generate_business_summary(user_question, result_df)
            st.info(f"💡 {summary_text}")

            st.subheader("Result")
            st.dataframe(result_df, width="stretch")

            render_visualization(user_question, result_df)

            st.session_state.history.insert(0, {
                "question": user_question,
                "sql": sql_query,
                "result": result_df,
                "summary": summary_text
            })

        except ValueError as e:
            st.error(f"🚫 {e}")
        except Exception as e:
            st.error(f"Something went wrong running this query: {e}")

# ---------- QUERY HISTORY DISPLAY ----------
if st.session_state.history:
    st.divider()
    st.subheader("🕒 Query History")
    for i, entry in enumerate(st.session_state.history[:5]):
        with st.expander(f"{entry['question']}"):
            st.code(entry["sql"], language="sql")
            st.caption(entry.get("summary", ""))
            st.dataframe(entry["result"], width="stretch")