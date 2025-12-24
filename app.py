import streamlit as st
from datetime import datetime
from docx import Document
import os
import requests

# -------------------- Page Config --------------------
st.set_page_config(page_title="WriteWise AI", layout="centered")

st.title("📝 WriteWise – Startup Blog Generator")
st.write("Generate SEO blogs, ideas, and rewrites using AI")

# -------------------- Setup --------------------
os.makedirs("outputs", exist_ok=True)

# -------------------- UI --------------------
mode = st.selectbox(
    "Choose content type",
    ["Blog Ideas", "Full SEO Blog", "Rewrite Content"]
)

topic = st.text_area("Enter topic or content")
keywords = st.text_input("SEO Keywords (comma separated)")
tone = st.selectbox("Select tone", ["Professional", "Casual", "Persuasive"])

# -------------------- Groq API Call --------------------
def call_groq(prompt: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        st.error("❌ GROQ_API_KEY is missing in Streamlit Secrets.")
        st.stop()

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a professional startup content writer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 600
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        st.error("❌ Network error while calling Groq API")
        st.code(str(e))
        st.stop()

    if response.status_code != 200:
        st.error(f"❌ Groq API Error {response.status_code}")
        st.code(response.text)
        st.stop()

    data = response.json()

    if "choices" not in data or not data["choices"]:
        st.error("❌ Invalid response from Groq API")
        st.code(data)
        st.stop()

    return data["choices"][0]["message"]["content"]

# -------------------- Generate Button --------------------
if st.button("Generate Content"):
    if not topic:
        st.warning("Please enter topic or content.")
    else:
        if mode == "Blog Ideas":
            prompt = f"""
            Generate 10 high-quality blog ideas for startups.

            Topic: {topic}
            SEO Keywords: {keywords}
            Tone: {tone}
            """

        elif mode == "Full SEO Blog":
            prompt = f"""
            Write a 400–500 word SEO-optimized blog for a startup.

            Topic: {topic}
            SEO Keywords: {keywords}
            Tone: {tone}

            Include:
            - Introduction
            - Headings
            - Conclusion
            """

        else:  # Rewrite
            prompt = f"""
            Rewrite the following content to be SEO-optimized and engaging
            for startup audiences.

            Content:
            {topic}

            SEO Keywords: {keywords}
            Tone: {tone}
            """

        with st.spinner("Generating content..."):
            output = call_groq(prompt)

        st.success("✅ Content generated!")
        st.text_area("Generated Content", output, height=400)

        # -------------------- Save Files --------------------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_path = f"outputs/content_{timestamp}.txt"
        docx_path = f"outputs/content_{timestamp}.docx"

        with open(txt_path, "w") as f:
            f.write(output)

        doc = Document()
        doc.add_heading("Generated Content", level=1)
        for line in output.split("\n"):
            doc.add_paragraph(line)
        doc.save(docx_path)

        # -------------------- Downloads --------------------
        st.download_button(
            "Download TXT",
            output,
            file_name=f"content_{timestamp}.txt"
        )

        with open(docx_path, "rb") as f:
            st.download_button(
                "Download DOCX",
                f,
                file_name=f"content_{timestamp}.docx"
            )

