# Healthcare AI Assistant

A simple healthcare-focused assistant that can:

- answer general medical questions
- summarize clinical documents or notes
- generate a structured patient handoff for doctors and nurses
- flag urgent symptoms and encourage professional care when needed

## Run locally

1. Open a terminal in this folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```
4. Open the URL shown in the terminal.

## Notes

This app is intended for informational use only. It does not replace clinical judgment. In urgent or emergency situations, seek immediate medical care.

If you have an OpenAI API key, set `OPENAI_API_KEY` before launching the app to enable AI-generated answers.
