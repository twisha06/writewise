import streamlit as st
from datetime import datetime
from docx import Document
import os
import requests

# -------------------- Page Config --------------------
st.set_page_config(page_title="WriteWise", layout="centered")

st.title("WriteWise")
st.caption("Thoughtful writing for startups — clear, original, and ready to publish.")
st.markdown("> WriteWise helps you think through ideas, not just fill pages.")

# -------------------- Setup --------------------
os.makedirs("outputs", exist_ok=True)

# -------------------- UI --------------------
mode = st.selectbox(
    "What would you like to work on today?",
    [
        "Brainstorm blog ideas",
        "Write a complete blog",
        "Refine existing content"
    ]
)

topic = st.text_area(
    "Your topic or draft",
    placeholder="e.g. How early-stage startups can use AI without overengineering"
)

keywords = st.text_input(
    "Optional keywords",
    placeholder="startup growth, AI tools, productivity"
)

tone = st.selectbox(
    "Writing style",
    ["Clear & professional", "Conversational", "Persuasive"]
)

# -------------------- Groq API Call --------------------
def call_groq(prompt: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        st.error("Missing API configuration. Please try again later.")
        st.stop()

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You write like a thoughtful human editor. "
                    "Your tone is natural, concise, and clear. "
                    "You avoid generic AI phrases, buzzwords, and filler. "
                    "You write for real startup founders and teams."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 600
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.RequestException:
        st.error("Network issue while preparing the draft. Please try again.")
        st.stop()

    if response.status_code != 200:
        st.error("Something went wrong while preparing your draft.")
        st.code(response.text)
        st.stop()

    data = response.json()

    if "choices" not in data or not data["choices"]:
        st.error("Unexpected response. Please try again.")
        st.stop()

    return data["choices"][0]["message"]["content"]

# -------------------- Generate Button --------------------
if st.button("Create draft"):
    if not topic:
        st.warning("Start by adding a topic or a rough draft.")
    else:
        if mode == "Brainstorm blog ideas":
            prompt = f"""
            Suggest 8–10 thoughtful blog ideas for a startup audience.

            Topic focus:
            {topic}

            Optional keywords:
            {keywords}

            Writing style:
            {tone}

            The ideas should feel practical, specific, and worth reading.
            """

        elif mode == "Write a complete blog":
            prompt = f"""
            Write a clear, well-structured blog post (400–500 words)
            aimed at startup founders or small teams.

            Topic:
            {topic}

            Optional keywords:
            {keywords}

            Writing style:
            {tone}

            The writing should feel human, grounded, and easy to follow.
            Include an introduction, section headings, and a short conclusion.
            """

        else:  # Refine existing content
            prompt = f"""
            Edit and refine the following draft.

            Improve clarity, flow, and tone without sounding artificial.
            Keep the voice human and direct.

            Draft:
            {topic}

            Optional keywords:
            {keywords}

            Writing style:
            {tone}
            """

        with st.spinner("Putting together a thoughtful draft…"):
            output = call_groq(prompt)

        st.success("Draft ready. Feel free to tweak or download.")

        st.text_area(
            "Your draft",
            output,
            height=400
        )

        # -------------------- Save Files --------------------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_path = f"outputs/draft_{timestamp}.txt"
        docx_path = f"outputs/draft_{timestamp}.docx"

        with open(txt_path, "w") as f:
            f.write(output)

        doc = Document()
        doc.add_heading("Draft", level=1)
        for line in output.split("\n"):
            doc.add_paragraph(line)
        doc.save(docx_path)

        # -------------------- Downloads --------------------
        st.download_button(
            "Download as text",
            output,
            file_name=f"draft_{timestamp}.txt"
        )

        with open(docx_path, "rb") as f:
            st.download_button(
                "Download as Word file",
                f,
                file_name=f"draft_{timestamp}.docx"
            )

