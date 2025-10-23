import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page setup
st.set_page_config(page_title="Code Quality Progress Tracker", layout="wide")

# Title
st.markdown(
    """
    <h1 style='font-size: 2.3em; font-weight: 700; display: flex; align-items: center;'>
        📈 Code Quality Progress Tracker
    </h1>
    <p style='color: #5f6368;'>Track and visualize your code review progress across all languages over time.</p>
    """,
    unsafe_allow_html=True,
)

# Initialize session state to store progress data
if "data" not in st.session_state:
    st.session_state["data"] = []

# Input section
st.markdown("### ✏️ Add New Review Entry")

col1, col2 = st.columns([2, 1])
with col1:
    file_name = st.text_input("Enter file name:", placeholder="example: index.html or Main.java or script.js")
with col2:
    score = st.slider("Select Code Quality Score (0-10):", 0.0, 10.0, 5.0, 0.1)

add_button = st.button("➕ Add Review Entry", use_container_width=True)

if add_button:
    if file_name:
        st.session_state["data"].append({
            "file": file_name.strip(),
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"✅ Added review entry for **{file_name}** with score **{score}/10**")
    else:
        st.warning("⚠️ Please enter a file name before adding an entry.")

st.markdown("---")

# If data exists, display chart
if st.session_state["data"]:
    df = pd.DataFrame(st.session_state["data"])

    # Create a smooth curved line chart with markers
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["score"],
        mode="lines+markers",
        line=dict(color="#7F56D9", width=4, shape="spline"),  # pastel purple line
        marker=dict(
            size=10,
            color="#B692F6",
            line=dict(width=2, color="white")
        ),
        hovertemplate="<b>%{text}</b><br>Score: %{y}/10<br>Date: %{x}<extra></extra>",
        text=df["file"]
    ))

    # Add an average line
    avg_score = df["score"].mean()
    fig.add_hline(
        y=avg_score,
        line_dash="dot",
        annotation_text=f"Avg: {avg_score:.2f}",
        annotation_position="top left",
        line_color="#FFB74D"
    )

    # Update layout for a modern look
    fig.update_layout(
        title=dict(
            text="📊 Your Code Quality Progress Over Time",
            font=dict(size=22, family="Segoe UI", color="#333"),
            x=0.02
        ),
        xaxis_title="🗓️ Date",
        yaxis_title="💯 Score (0-10)",
        template="plotly_white",
        height=480,
        margin=dict(l=40, r=40, t=70, b=40),
        paper_bgcolor="rgba(250, 250, 255, 1)",
        plot_bgcolor="rgba(255, 255, 255, 1)",
        font=dict(family="Segoe UI", size=14, color="#444"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Data table
    with st.expander("📋 View Review History"):
        st.dataframe(df[::-1].reset_index(drop=True), use_container_width=True)

else:
    st.info("💡 No reviews yet. Add your first entry to start tracking your progress!")
