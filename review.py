import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load environment and configure Gemini
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file!")

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(
    MODEL_NAME,
    generation_config={"temperature": 0, "top_p": 1, "top_k": 1}  # ✅ deterministic output
)

# 🔍 Extract realistic, stable scores
def extract_metrics(review_text: str):
    metrics = {
        "readability": 5,
        "efficiency": 5,
        "maintainability": 5,
        "bugs": 5
    }

    # Flexible pattern matching (handles multiple phrasing styles)
    patterns = {
        "readability": r"readability[^0-9]*(\d{1,2})",
        "efficiency": r"efficienc[^0-9]*(\d{1,2})",
        "maintainability": r"maintain[^0-9]*(\d{1,2})",
        "bugs": r"bugs?[^0-9]*(\d{1,2})"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, review_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            metrics[key] = max(1, min(score, 10))  # normalize 1–10

    return metrics


def review_code_with_gemini(code: str):
    """
    ✅ Reviews code and returns:
    - Detailed feedback
    - Optimized version
    - Realistic, consistent metrics (1–10)
    """
    try:
        prompt = f"""
        You are a professional software engineer and senior code reviewer.
        Review the following code for:
        - Bugs and errors
        - Code readability
        - Efficiency
        - Maintainability
        - Best practices

        Provide the review in detail, and at the end of the review include numeric scores (1–10)
        for each of these categories in this format:
        Readability: x/10
        Efficiency: x/10
        Maintainability: x/10
        Bugs: x/10

        Then provide the optimized version of the same code below.

        Format exactly like this:
        REVIEW:
        (your detailed feedback)

        OPTIMIZED CODE:
        (improved version)

        --- Code Start ---
        {code}
        --- Code End ---
        """

        # 🔹 Get Gemini response
        response = model.generate_content(prompt)
        text = response.text.strip() if hasattr(response, "text") else "⚠️ No response from model."

        # 🔹 Extract review + optimized code
        parts = text.split("OPTIMIZED CODE:")
        review = parts[0].replace("REVIEW:", "").strip() if len(parts) > 0 else text
        optimized_code = parts[1].strip() if len(parts) > 1 else "No optimized code provided."

        # 🔹 Extract consistent numeric metrics
        metrics = extract_metrics(review)

        return review, optimized_code, metrics

    except Exception as e:
        return f"⚠️ Error while reviewing code: {str(e)}", "", {
            "readability": 0,
            "efficiency": 0,
            "maintainability": 0,
            "bugs": 0
        }
