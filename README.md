# Smart CV Analyzer

A Streamlit application for uploading a CV (PDF), pasting a job description, and generating a match score with missing skills detection and ATS improvement suggestions.

## Features

- Upload CV as PDF
- Paste job description text
- Calculate a job fit match score
- Detect missing skills
- Receive ATS-friendly resume suggestions

## Setup

1. Create a Python virtual environment:

```bash
python -m venv .venv
```

2. Activate the environment:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set your OpenAI API key:

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

5. Run the app:

```bash
streamlit run app.py
```

## Notes

- OpenAI is optional for ATS suggestions, but recommended for the best results.
- The app uses `PyPDF` to extract text from resumes.
- If no API key is provided, local matching and missing skills detection still work.
