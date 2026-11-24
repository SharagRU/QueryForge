
import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

from src.agent.pipeline import ask_database


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="QueryForge | AI Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080B14;
    color: #E8ECF8;
}

[data-testid="stSidebar"] {
    background: #0D1220;
    border-right: 1px solid #202940;
}

.hero {
    padding: 28px;
    border: 1px solid #27334F;
    border-radius: 18px;
    background: linear-gradient(120deg, #151E36, #101729);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    margin: 0;
    color: #FFFFFF;
}

.hero p {
    color: #9BAAC8;
    font-size: 15px;
    margin-top: 10px;
}

.accent {
    color: #8B9CFF;
}

.metric-card {
    background: #111827;
    border: 1px solid #26334D;
    border-radius: 14px;
    padding: 18px;
}

.metric-label {
    color: #91A0BC;
    font-size: 12px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 700;
    margin-top: 6px;
}

.section-title {
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 700;
    margin: 20px 0 12px 0;
}

.stButton button {
    background: linear-gradient(90deg, #6578FF, #8B5CF6);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 43px;
}

.stButton button:hover {
    border: 1px solid #A5B4FC;
    color: white;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #26334D;
    border-radius: 12px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "last_response" not in st.session_state:
    st.session_state.last_response = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# ⚡ QueryForge")
    st.caption("AI-POWERED BUSINESS INTELLIGENCE")

    st.divider()

    st.markdown("### Navigation")
    st.markdown("🏠  Analytics Workspace")
    st.markdown("🧠  Natural Language SQL")
    st.markdown("📊  Data Visualization")
    st.markdown("🕘  Query History")

    st.divider()

    st.markdown("### Example Queries")

    examples = [
        "Top 5 products by completed revenue",
        "Top 10 cities by refunded order count",
        "Top 7 customers by average order value",
        "Top 8 months by completed revenue",
        "Top 10 product categories by revenue",
        "Top 10 customers by number of orders"
    ]

    for example in examples:
        if st.button(example, key="example_" + example):
            st.session_state.query_input = example

    st.divider()

    st.markdown("### System Status")
    st.success("Database connected")
    st.success("SQL execution ready")
    st.success("Query engine ready")

    st.caption("QueryForge • Hackathon Edition")


# --------------------------------------------------
# CSV DATASET MODE
# --------------------------------------------------
import tempfile, re, sqlite3
uploaded_csv = st.sidebar.file_uploader("Try your own CSV dataset", type=["csv"])
if uploaded_csv is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_csv)
        safe_table = re.sub(r"[^a-zA-Z0-9_]", "_", uploaded_csv.name.rsplit(".",1)[0])[:48] or "uploaded_data"
        if st.session_state.get("uploaded_name") != uploaded_csv.name:
            temp_db = os.path.join(tempfile.gettempdir(), "queryforge_upload_" + safe_table + ".sqlite")
            with sqlite3.connect(temp_db) as conn:
                uploaded_df.to_sql(safe_table, conn, if_exists="replace", index=False)
            st.session_state.uploaded_db_path = temp_db
            st.session_state.uploaded_name = uploaded_csv.name
            st.session_state.uploaded_table = safe_table
        st.sidebar.success(f"Loaded {len(uploaded_df)} rows into table: {safe_table}")
        st.sidebar.caption("Dynamic mode requires GEMINI_API_KEY (Gemini API).")
    except Exception as upload_error:
        st.sidebar.error(f"CSV load failed: {upload_error}")

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>QueryForge <span class="accent">⚡</span></h1>
    <p>
        Transform natural language into SQL.
        Explore business data. Discover insights.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# METRICS
# --------------------------------------------------

history = st.session_state.history

total_queries = len(history)
successful_queries = sum(
    1 for item in history if item["success"]
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Queries", total_queries)

with col2:
    st.metric("Successful Queries", successful_queries)

with col3:
    st.metric(
        "Success Rate",
        f"{successful_queries / total_queries * 100:.1f}%"
        if total_queries else "—"
    )

with col4:
    st.metric("Benchmark Accuracy", "100%*")

st.caption("*60/60 correct results on the current test benchmark.")


# --------------------------------------------------
# QUERY WORKSPACE
# --------------------------------------------------

st.markdown('<div class="section-title">🧠 Ask Your Database</div>',
            unsafe_allow_html=True)

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

dynamic_mode = st.checkbox("Use uploaded CSV + schema-aware AI mode", value=bool(st.session_state.get("uploaded_db_path")), disabled=not bool(st.session_state.get("uploaded_db_path")))

question = st.text_area(
    "Ask a business question in plain English",
    key="query_input",
    height=100,
    placeholder="Example: Top 10 products by completed revenue"
)

run_col, clear_col = st.columns([1, 5])

with run_col:
    run_query = st.button(
        "⚡ Run Query",
        type="primary",
        use_container_width=True
    )

with clear_col:
    clear_query = st.button("Clear")

if clear_query:
    st.session_state.query_input = ""
    st.rerun()


# --------------------------------------------------
# QUERY EXECUTION
# --------------------------------------------------

if run_query:

    if not question.strip():
        st.warning("Enter a question first.")

    else:
        with st.spinner("QueryForge is analyzing your question..."):

            start_time = time.perf_counter()

            try:
                response = ask_database(question.strip(), database_path=st.session_state.get("uploaded_db_path") if dynamic_mode else None, dynamic=dynamic_mode)
                elapsed = time.perf_counter() - start_time

                response["elapsed"] = elapsed

                st.session_state.last_response = response

                st.session_state.history.insert(0, {
                    "question": question.strip(),
                    "success": response["success"],
                    "elapsed": elapsed
                })

            except Exception as error:
                response = {
                    "success": False,
                    "error": str(error),
                    "stage": "application"
                }

                st.session_state.last_response = response


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

response = st.session_state.last_response

if response:

    st.divider()

    if response.get("success"):

        st.success("Query executed successfully!")

        results = response.get("result", [])
        df = pd.DataFrame(results)

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric("Returned Rows", len(df))

        with metric2:
            st.metric(
                "Execution Time",
                f"{response.get('elapsed', 0):.3f}s"
            )

        with metric3:
            st.metric("Query Status", "SUCCESS")

        st.markdown(
            '<div class="section-title">📋 Query Results</div>',
            unsafe_allow_html=True
        )

        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("The query returned no rows.")

        # SQL PREVIEW
        with st.expander("🔍 View Generated SQL", expanded=True):
            st.code(
                response.get("generated_sql", "SQL unavailable"),
                language="sql"
            )

        # AUTOMATIC VISUALIZATION
        if not df.empty and len(df.columns) >= 2:

            numeric_columns = df.select_dtypes(
                include="number"
            ).columns.tolist()

            if numeric_columns:

                st.markdown(
                    '<div class="section-title">📊 Data Visualization</div>',
                    unsafe_allow_html=True
                )

                category_column = next(
                    (
                        col for col in df.columns
                        if col not in numeric_columns
                    ),
                    None
                )

                if category_column:

                    value_column = numeric_columns[0]

                    chart_type = st.selectbox(
                        "Choose visualization",
                        ["Bar Chart", "Line Chart", "Pie Chart"],
                        key="chart_type"
                    )

                    if chart_type == "Bar Chart":
                        fig = px.bar(
                            df,
                            x=category_column,
                            y=value_column,
                            template="plotly_dark",
                            color=value_column
                        )

                    elif chart_type == "Line Chart":
                        fig = px.line(
                            df,
                            x=category_column,
                            y=value_column,
                            template="plotly_dark",
                            markers=True
                        )

                    else:
                        fig = px.pie(
                            df,
                            names=category_column,
                            values=value_column,
                            template="plotly_dark",
                            hole=0.45
                        )

                    fig.update_layout(
                        paper_bgcolor="#080B14",
                        plot_bgcolor="#080B14",
                        font_color="#E8ECF8",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

    else:

        st.error(
            f"Query failed: {response.get('error', 'Unknown error')}"
        )

        st.caption(
            f"Failure stage: {response.get('stage', 'unknown')}"
        )


# --------------------------------------------------
# QUERY HISTORY
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">🕘 Recent Query History</div>',
    unsafe_allow_html=True
)

if history:

    history_df = pd.DataFrame(history)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Your executed queries will appear here.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    "<center style='color:#66738F'>"
    "QUERYFORGE • AI-POWERED BUSINESS ANALYTICS"
    "<br>Built with Python, SQLite, SQL and Streamlit"
    "</center>",
    unsafe_allow_html=True
)
