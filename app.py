import os
import streamlit as st
from analyzer import analyze_resume, extract_text_from_pdf

st.set_page_config(
    page_title="Smart CV Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

st.markdown("<div class='card'>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1], gap="large")
with col1:
    st.markdown("# Smart CV Analyzer")
    st.markdown(
        "<p class='description'>Use AI-driven resume analysis to identify gaps, match your CV to job requirements, and improve ATS compatibility.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top: 1.75rem;'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload CV (PDF)",
        type=["pdf"],
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    job_description = st.text_area("Paste Job Description", height=300)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div style='padding: 1.2rem 1.5rem; background: #eef2ff; border-radius: 24px; height: 100%;'>", unsafe_allow_html=True)
    st.markdown("## Instructions")
    st.markdown(
        "- Upload your CV as a PDF file.\n"
        "- Paste the job description or role requirements.\n"
        "- Click Analyze to receive a match score and optimization tips."
    )
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    st.info("Ensure your submitted resume emphasizes skills, achievements, and relevant keywords.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

analyze_button = st.button("Analyze")

if analyze_button:
    if not uploaded_file and not job_description.strip():
        st.warning("Please upload a CV PDF and paste a job description.")
    elif not uploaded_file:
        st.warning("Please upload a CV PDF to analyze.")
    elif not job_description.strip():
        st.warning("Please paste a job description to analyze.")
    else:
        with st.spinner("Analyzing resume and job description..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume(resume_text, job_description)

        st.markdown("<div class='card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        st.markdown("## Match Summary")
        st.markdown(
            f"<div class='metric-container'><span class='highlight'>Match score:</span> <strong>{result['match_score']}%</strong></div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("### Detected Skills")
            st.write("**Resume skills:**", ", ".join(sorted(result["resume_skills"])) or "No skills detected")
            st.write("**Job skills:**", ", ".join(sorted(result["job_skills"])) or "No skills detected")

        with col2:
            st.markdown("### Missing Skills")
            if result["missing_skills"]:
                st.write(", ".join(sorted(result["missing_skills"])))
            else:
                st.success("No missing skills detected.")

        st.markdown("---")
        st.markdown("### ATS Suggestions")
        if result["ats_suggestions"]:
            for idx, suggestion in enumerate(result["ats_suggestions"], start=1):
                st.write(f"**{idx}.** {suggestion}")
        else:
            st.info("Automatic suggestions are not available. Ensure your API key is configured for enhanced guidance.")

        st.markdown("---")
        st.markdown("### Resume Text Preview")
        st.text_area("Extracted Resume Text", resume_text, height=300)
        st.markdown("</div>", unsafe_allow_html=True)
