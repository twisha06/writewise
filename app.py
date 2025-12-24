import streamlit as st
from datetime import datetime
from docx import Document
import os
from groq import Groq

# Page config
st.set_page_config(page_title="WriteWise AI", layout="centered")

st.title("📝 WriteWise – Startup Blog Generator")
st.write("Generate SEO blogs, ideas, and rewrites using AI")

# Groq client (API key from Streamlit Secrets)
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
client = Groq()

# Ensure outputs folder exists
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# UI inputs
mode = st.selectbox(
    "Choose content type",
    ["Blog Ideas", "Full SEO Blog", "Rewrite Content"]
)

topic = st.text_area("Enter topic or content")
keywords = st.text_input("SEO Keywords (comma separated)")
tone = st.selectbox("Select tone", ["Professional", "Casual", "Persuasive"])

# Generate button
if st.button("Generate Content"):
    if not topic:
        st.warning("Please enter topic or content")
    else:
        # Prompt building
        if mode == "Blog Ideas":
            prompt = f"""
            Generate 10 high-quality blog ideas for startups.

            Topic: {topic}
            SEO Keywords: {keywords}
            Tone: {tone}
            """

        elif mode == "Full SEO Blog":
            prompt = f"""
            Write a 700-word SEO-optimized blog for a startup.

            Topic: {topic}
            SEO Keywords: {keywords}
            Tone: {tone}

            Include:
            - SEO-friendly headings
            - Introduction
            - Conclusion
            - Natural keyword usage
            """

        else:
            prompt = f"""
            Rewrite the following content to be SEO-optimized and engaging
            for startup audiences.

            Content:
            {topic}

            SEO Keywords: {keywords}
            Tone: {tone}
            """

        with st.spinner("Generating content..."):
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional startup content writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

        output = response.choices[0].message.content

        st.success("Content generated!")
        st.text_area("Generated Content", output, height=400)

        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = f"outputs/content_{timestamp}.txt"
        docx_file = f"outputs/content_{timestamp}.docx"

        with open(txt_file, "w") as f:
            f.write(output)

        doc = Document()
        doc.add_heading("Generated Content", level=1)
        for line in output.split("\n"):
            doc.add_paragraph(line)
        doc.save(docx_file)

        st.download_button(
            "Download TXT",
            output,
            file_name=f"content_{timestamp}.txt"
        )

        with open(docx_file, "rb") as f:
            st.download_button(
                "Download DOCX",
                f,
                file_name=f"content_{timestamp}.docx"
            )

