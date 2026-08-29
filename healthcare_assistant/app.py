import os
import re
from typing import Optional

import streamlit as st
import openai



URGENT_PATTERNS = [
    "chest pain",
    "trouble breathing",
    "severe bleeding",
    "fainting",
    "confusion",
    "severe headache",
    "stroke",
    "unconscious",
    "suicidal",
    "high fever",
    "difficulty breathing",
    "shortness of breath",
]

#Sidebar with Patient Information
st.sidebar.title("Patient Information")
name = st.sidebar.text_input("Name: [Enter patient name]")
age = st.sidebar.number_input("Age: [Enter patient age]", min_value=0, max_value=150, step=1)
sex = st.sidebar.selectbox("Sex: [Enter patient sex]", options=["Male", "Female", "Other"])
medical_history = st.sidebar.text_area("Medical History: [Enter relevant medical history]")
current_medications = st.sidebar.text_area("Current Medications: [Enter current medications]")
st.sidebar.button("Submit")




def generate_openai_response(prompt: str) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical information assistant. Provide general, cautious health information. "
                        "Do not diagnose, do not provide treatment directives beyond general, non-urgent guidance. "
                        "Always encourage contacting a qualified clinician for serious symptoms."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return getattr(response, "output_text", None) or response.choices[0].message.content
    except Exception:
        return None


def answer_medical_question(question: str) -> str:
    if not question or not question.strip():
        return "Please enter a medical question so I can help."

    prompt = f"Answer this medical question in plain language and keep it general. Question: {question}"
    ai_response = generate_openai_response(prompt)
    if ai_response:
        return ai_response.strip()

    q = question.lower()
    urgent = any(pattern in q for pattern in URGENT_PATTERNS)
    if urgent:
        return (
            "This could be urgent. Seek urgent medical evaluation now or call emergency services if symptoms are severe, "
            "rapidly worsening, or accompanied by chest pain, trouble breathing, confusion, fainting, or severe bleeding. "
            "I can provide general information, but I cannot replace professional medical assessment."
        )

    if "fever" in q:
        return (
            "For a fever, the general approach is fluids, rest, and monitoring symptoms. High fever, persistent fever, "
            "difficulties breathing, confusion, stiff neck, or a fever in a newborn should be assessed by a doctor promptly."
        )

    if "cough" in q:
        return (
            "A cough can be caused by colds, allergies, asthma, reflux, or infections. Seek care if it lasts more than 2-3 weeks, "
            "you have fever, chest pain, shortness of breath, coughing blood, or worsening symptoms."
        )

    if "headache" in q:
        return (
            "Headaches are often mild and temporary, but sudden severe headache, weakness, confusion, fever, or vomiting should be evaluated urgently. "
            "Keep hydration and avoid overstimulation while monitoring symptoms."
        )

    if "pain" in q:
        return (
            "Pain severity, duration, and location matter. If pain is severe, sudden, or accompanied by chest pain, shortness of breath, fever, swelling, or weakness, seek prompt medical care."
        )

    return (
        "I can provide general health information, but this is not a diagnosis. For persistent, worsening, or unusual symptoms, "
        "a clinician should assess the situation. If symptoms are severe or rapidly worsening, seek urgent evaluation."
    )


def summarize_document(document_text: str) -> str:
    if not document_text or not document_text.strip():
        return "Please paste a patient note or document for summarization."

    prompt = (
        "Summarize this medical document in clear and concise language for a clinician. Include: "
        "1) main medical issues, 2) current symptoms, 3) key observations, 4) follow-up or risk concerns. "
        "Document:\n"
        f"{document_text}"
    )
    ai_response = generate_openai_response(prompt)
    if ai_response:
        return ai_response.strip()

    cleaned = re.sub(r"\s+", " ", document_text).strip()
    if len(cleaned) < 50:
        return "The provided text is too short to summarize meaningfully."

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    summary_lines = [
        "Main clinical concerns:",
        "- Review the documented symptoms, associated duration, and severity.",
        "- Note any known diagnoses, recent treatments, or medication changes.",
        "- Identify key risk factors such as age, fever, oxygen concerns, or worsening condition.",
        "",
        "Short summary:",
        f"- The document describes {min(len(sentences), 3)} relevant clinical observations, including symptom progression and current care status.",
        "- The key follow-up concern is whether the patient is stable, improving, or showing red-flag symptoms requiring urgent assessment.",
        "- Additional clinician review may be needed if there are abnormal vitals, worsening pain, or concerning lab or imaging findings.",
    ]
    return "\n".join(summary_lines)

uploaded_files = st.file_uploader("Upload a clinical document (PDF, DOCX, or TXT) for summarization:", type=["pdf", "docx", "txt"])
for uploaded_file in uploaded_files or []:
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader

            pdf_reader = PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            from docx import Document

            doc = Document(uploaded_file)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        else:
            text = file_content.decode("utf-8", errors="ignore")

        summary = summarize_document(text)
        st.text_area("Document Summary", summary, height=220)


def build_handoff_note(patient_name: str, symptoms: str, history: str, vitals: str, meds: str) -> str:
    patient_name = patient_name.strip() or "Patient"
    symptoms = symptoms.strip() or "No symptom details provided"
    history = history.strip() or "No past medical history provided"
    vitals = vitals.strip() or "No vitals provided"
    meds = meds.strip() or "No medication list provided"

    prompt = (
        "Create a concise clinician handoff note using this patient information. Include assessment, symptom summary, "
        "vitals, PMH, current medications, concerns, and suggested action. Format as a structured note. "
        f"Patient: {patient_name}\nSymptoms: {symptoms}\nHistory: {history}\nVitals: {vitals}\nMedications: {meds}"
    )
    ai_response = generate_openai_response(prompt)
    if ai_response:
        return ai_response.strip()

    return (
        f"Handoff Note: {patient_name}\n"
        "\n"
        "Reason for handoff:\n"
        f"- Symptoms reported: {symptoms}\n"
        "\n"
        "Clinical background:\n"
        f"- Relevant history: {history}\n"
        f"- Vitals: {vitals}\n"
        f"- Current medications: {meds}\n"
        "\n"
        "Assessment:\n"
        "- Patient is being transitioned for clinician review.\n"
        "- Monitor for worsening pain, fever, respiratory symptoms, confusion, or signs of acute deterioration.\n"
        "\n"
        "Action requested:\n"
        "- Please evaluate stability, confirm diagnosis, and determine whether urgent assessment or ongoing observation is needed.\n"
    )


st.set_page_config(page_title="Healthcare AI Assistant", page_icon="🩺")

st.title("Healthcare AI Assistant")
st.caption("General clinical support for questions, document summaries, and clinician handoffs.")
st.warning("This tool is for informational use only and does not replace professional medical judgment.")

main_tab, summary_tab, handoff_tab = st.tabs(["Ask a question", "Summarize document", "Doctor / Nurse handoff"])

with main_tab:
    st.subheader("Medical question")
    question = st.text_area("Enter a question about symptoms, care, or common health concerns:", height=150)
    if st.button("Get answer"):
        result = answer_medical_question(question)
        st.markdown(result)

with summary_tab:
    st.subheader("Clinical document summary")
    raw_text = st.text_area("Paste patient notes, visit summaries, or a chart excerpt:", height=220)
    if st.button("Summarize note"):
        summary = summarize_document(raw_text)
        st.text_area("Summary", summary, height=220)

with handoff_tab:
    st.subheader("Clinician handoff note")
    patient_name = st.text_input("Patient name")
    symptoms = st.text_area("Current symptoms")
    history = st.text_area("Past medical history")
    vitals = st.text_area("Vitals and observations")
    meds = st.text_area("Current medications")
    if st.button("Generate handoff"):
        note = build_handoff_note(patient_name, symptoms, history, vitals, meds)
        st.text_area("Handoff note", note, height=260)

st.markdown("---")
st.info("Urgent red flags: chest pain, trouble breathing, severe bleeding, confusion, fainting, or rapidly worsening symptoms should prompt immediate evaluation.")
