import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_genai():
    """Initializes the Google Generative AI model."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY environment variable is not set.")
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Error initializing Google Generative AI: {e}")
        return None

# Initialize the model once when the application starts
model = initialize_genai()

def analyze_resume(resume_text, job_role):
    """
    Analyzes a resume against a job role using the Gemini AI.
    """
    if not model:
        return "Error: AI model is not initialized. Please check your API key."

    prompt = f"""
    As a senior HR reviewer and career coach at a top technology firm, please provide a professional analysis of the following resume for the job role of "{job_role}".

    Your response should be structured as a real HR professional would provide feedback to a candidate.

    **Resume Score:**
    Provide a score out of 100, based on relevance, skills, structure, and overall presentation.

    **Strengths:**
    Identify 2-3 key strengths of the resume that align with the target role.

    **Areas for Improvement:**
    List specific, actionable suggestions for what the candidate can do to improve their resume. Focus on clarity, professionalism, and alignment with the job description.

    **Missing Skills/Keywords:**
    Based on the job role of "{job_role}", list any critical skills or keywords that are missing from the resume.

    **Resume Text to Analyze:**
    {resume_text}

    Please provide a comprehensive and supportive analysis.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content from AI: {e}")
        return f"An error occurred during AI analysis: {e}"