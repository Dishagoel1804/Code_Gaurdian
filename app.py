import streamlit as st
from review import review_code_with_gemini
import io
import re
import matplotlib.pyplot as plt
import time
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ----------------- Page Config -----------------
st.set_page_config(page_title="", layout="wide")

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to:", ["AI Code Reviewer", "Progress Tracker"])

# ----------------- Sidebar Settings -----------------
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Choose Theme:", ["Light 🌞", "Dark 🌙"])

# Theme colors
bg_color = "#f9f9f9" if "Light" in theme else "#0e1117"
text_color = "#000000" if "Light" in theme else "#ffffff"
accent_color = "#0066cc" if "Light" in theme else "#4a90e2"
card_color = "#ffffff" if "Light" in theme else "#1e1e1e"

# ----------------- Custom CSS -----------------
st.markdown(
    f"""
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stTextArea textarea {{
            background-color: {card_color};
            color: {text_color};
            border-radius: 10px;
            border: 1px solid #444;
            font-family: "Consolas", monospace;
        }}
        .stButton button {{
            background-color: {accent_color};
            color: white;
            border-radius: 10px;
            font-weight: 600;
            transition: 0.3s;
        }}
        .stButton button:hover {{
            transform: scale(1.05);
            background-color: #0056b3;
        }}
        h1, h2, h3 {{
            color: {text_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------- Improved Score Calculation -----------------
def calculate_code_score(review_text: str, optimized_code: str) -> float:
    """
    Improved scoring logic based on review text + optimized code.
    """

    text = (review_text + " " + optimized_code).lower()

    # Positive and negative keyword weights
    positive = {
        "optimized": 1.5, "efficient": 1.3, "readable": 1.2, "maintainable": 1.2,
        "clean": 1.0, "good practice": 1.0, "modular": 1.1, "no bugs": 1.3,
        "works": 1.0, "improved": 1.1
    }
    negative = {
        "bug": -1.5, "error": -1.2, "inefficient": -1.3, "redundant": -1.0,
        "complex": -1.0, "bad": -1.1, "issue": -1.3, "not working": -1.5
    }

    base = 5.0
    score = base

    # Count keyword presence and adjust score
    for word, weight in positive.items():
        if word in text:
            score += weight
    for word, weight in negative.items():
        if word in text:
            score += weight  # negative weights will reduce score

    # Normalize
    score = max(0.0, min(10.0, round(score, 1)))
    return score


# ----------------- Chart Rendering -----------------
def render_chart_as_image_bytes(final_score: float):
    fig, ax = plt.subplots(figsize=(2, 2))
    plt.subplots_adjust(left=0, right=1, top=0.9, bottom=0)

    if final_score >= 8:
        color, label = '#4CAF50', '🌟 Excellent'
    elif final_score >= 5:
        color, label = '#FFD700', '👍 Good'
    else:
        color, label = '#FF6347', '⚠️ Needs Improvement'

    sizes = [final_score, max(0.0, 10 - final_score)]
    ax.pie(sizes, startangle=90, colors=[color, '#E0E0E0'],
           wedgeprops={'width': 0.35, 'edgecolor': 'white'})
    ax.text(0, 0, f"{final_score:.1f}/10", ha='center', va='center', fontsize=14, fontweight='bold')
    ax.axis('equal')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=80)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue(), label, color


# ----------------- Session State -----------------
if "progress_data" not in st.session_state:
    st.session_state.progress_data = []


# ===============================================================
# 🧠 PAGE 1 — AI CODE REVIEWER
# ===============================================================
if page == "AI Code Reviewer":
    st.title("🤖 CodeGuardian")
    st.caption("Analyze your code for quality, bugs, and readability.")

    uploaded_file = st.file_uploader(
        "📂 Upload your code file",
        type=["py", "js", "java", "cpp", "c", "html", "css", "ts", "go", "php", "rb", "htm"]
    )

    code_text = uploaded_file.read().decode("utf-8") if uploaded_file else ""
    st.markdown("### 🧾 Or paste your code below:")
    code_input = st.text_area("Your Code", code_text, height=300)

    if st.button("🚀 Review Code"):
        if code_input.strip():
            with st.spinner("🧠 Analyzing your code..."):
                review_result, optimized_code, metrics = review_code_with_gemini(code_input)


            st.success("✅ Code Review Complete!")

            # --- Calculate score ---
            score = calculate_code_score(review_result, optimized_code)
            chart_bytes, label, color = render_chart_as_image_bytes(score)

            # --- Layout ---
            col_chart, col_review = st.columns([1, 3])
            with col_chart:
                st.image(chart_bytes, width=220)
                st.markdown(f"<div style='text-align:center; color:{color}; font-weight:600'>{label}</div>", unsafe_allow_html=True)
            with col_review:
                st.markdown("### 🧩 Code Review:")
                st.markdown(review_result, unsafe_allow_html=False)
                st.markdown("### 🧠 Optimized Code:")
                st.code(optimized_code, language='python')

            # --- Progress Tracker ---
            st.session_state.progress_data.append({
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Score": score
            })

            # --- PDF Download ---
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            c.setFont("Helvetica", 10)
            y = 750
            for line in review_result.split("\n"):
                c.drawString(50, y, line)
                y -= 15
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = 750
            c.save()
            pdf_buffer.seek(0)

            st.download_button(
                label="📄 Download Review Report (PDF)",
                data=pdf_buffer,
                file_name="ai_code_review_report.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("⚠️ Please enter or upload some code first.")


# ===============================================================
# 📈 PAGE 2 — PROGRESS TRACKER
# ===============================================================
elif page == "Progress Tracker":
    st.title("📊 Progress Tracker")
    st.caption("Track your improvement over time with past review scores.")

    if not st.session_state.progress_data:
        st.info("No progress data yet. Review some code first! 🚀")
    else:
        df = pd.DataFrame(st.session_state.progress_data)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

        st.line_chart(df.set_index("Timestamp")["Score"])
        st.dataframe(df.sort_values("Timestamp", ascending=False), use_container_width=True)

        avg_score = df["Score"].mean()
        st.metric("Average Code Quality", f"{avg_score:.2f}/10")

        if st.button("🗑️ Clear Progress Data"):
            st.session_state.progress_data = []
            st.success("Progress data cleared successfully!")
