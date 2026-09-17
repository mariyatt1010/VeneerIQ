import streamlit as st
import plotly.express as px


def render_visualization(user_question, result_df):
    """
    Automatically picks and renders the most appropriate visualization,
    based on the shape of the result data and hints in the question text.
    """
    if result_df is None or result_df.empty:
        return

    question_lower = user_question.lower()
    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
    text_cols = result_df.select_dtypes(include="object").columns.tolist()
    date_like_cols = [c for c in result_df.columns if "date" in c.lower() or "month" in c.lower()]

    # Case 1: Single value result (e.g. "What is the total revenue?") -> KPI card
    if len(result_df) == 1 and len(numeric_cols) == 1 and len(result_df.columns) <= 2:
        value = result_df[numeric_cols[0]].iloc[0]
        st.metric(numeric_cols[0].replace("_", " ").title(), f"{value:,.2f}")
        return

    # Case 2: Has a date/month column -> Line chart (shows a trend over time)
    if date_like_cols and numeric_cols:
        fig = px.line(
            result_df, x=date_like_cols[0], y=numeric_cols[-1], markers=True,
            title=f"{numeric_cols[-1].replace('_', ' ').title()} over {date_like_cols[0].replace('_', ' ').title()}"
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    # Case 3: Question implies "share/breakdown" and few categories -> Pie chart
    share_keywords = ["share", "percentage", "distribution", "proportion", "breakdown"]
    if text_cols and numeric_cols and len(result_df) <= 8 and any(k in question_lower for k in share_keywords):
        fig = px.pie(
            result_df, names=text_cols[0], values=numeric_cols[-1],
            title=f"{numeric_cols[-1].replace('_', ' ').title()} by {text_cols[0].replace('_', ' ').title()}"
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    # Case 4: Default -> Bar chart (great for "top N", "by customer", "by category", rankings)
    if text_cols and numeric_cols and len(result_df) <= 25:
        fig = px.bar(
            result_df, x=text_cols[0], y=numeric_cols[-1],
            title=f"{numeric_cols[-1].replace('_', ' ').title()} by {text_cols[0].replace('_', ' ').title()}"
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    # Otherwise: no chart type clearly fits (e.g. too many rows, no numeric column) - skip silently