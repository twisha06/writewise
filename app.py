import streamlit as st
import subprocess
from datetime import datetime
from docx import Document
import os

# Page config
st.set_page_config(page_title="Startup Blog Bot", layout="centered")

st.title("📝 Startup Blog Content Generator")
st.write("Generate SEO blogs, ideas, and rewrites using AI")

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
        # Build prompt
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

        else:  # Rewrite Content
            prompt = f"""
            Rewrite the following content to be SEO-optimized and engaging
            for startup audiences.

            Content:
            {topic}

            SEO Keywords: {keywords}
            Tone: {tone}
            """

        # Run Ollama
        with st.spinner("Generating content..."):
            result = subprocess.run(
                ["ollama", "run", "llama3:8b", prompt],
                capture_output=True,
                text=True
            )

        output = result.stdout

        st.success("Content generated!")
        st.text_area("Generated Content", output, height=400)

        # File names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = f"outputs/content_{timestamp}.txt"
        docx_file = f"outputs/content_{timestamp}.docx"

        # Save TXT
        with open(txt_file, "w") as f:
            f.write(output)

        # Save DOCX
        doc = Document()
        doc.add_heading("Generated Content", level=1)
        for line in output.split("\n"):
            doc.add_paragraph(line)
        doc.save(docx_file)

        # Download buttons
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

