import streamlit as st
import requests
import zipfile
import os
import io

st.set_page_config(page_title="GitHub Integration Demo", layout="centered")
st.title("🐙 GitHub Repository Integration Demo")

st.markdown("Enter a public GitHub repo URL to fetch code files for review.")

github_url = st.text_input("🔗 Enter GitHub Repository URL:")

if st.button("📦 Fetch Repository"):
    if github_url.strip():
        try:
            user_repo = github_url.split("github.com/")[-1].rstrip("/")
            zip_url = f"https://github.com/{user_repo}/archive/refs/heads/main.zip"

            st.info("Downloading repository...")
            response = requests.get(zip_url)
            response.raise_for_status()

            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall("repo_files")

            st.success("✅ Repository downloaded successfully!")

            # List Python files
            py_files = []
            for root, dirs, files in os.walk("repo_files"):
                for file in files:
                    if file.endswith(".py"):
                        py_files.append(os.path.join(root, file))

            if py_files:
                selected_file = st.selectbox("📄 Select a file to view:", py_files)
                if selected_file:
                    with open(selected_file, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    st.code(code, language="python")
            else:
                st.warning("No Python files found in this repo.")
        except Exception as e:
            st.error(f"❌ Error fetching repository: {e}")
    else:
        st.warning("Please enter a valid GitHub repository URL.")
