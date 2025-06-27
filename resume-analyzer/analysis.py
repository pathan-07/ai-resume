import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')  # or use gemini-pro if preferred

def analyze_resume(resume_text, job_role):
    prompt = f"""
You are a senior HR reviewer and career coach at a top technology firm.

Please review the following resume for the job role of "{job_role}".
Write your response as a real HR would write feedback to a junior candidate.

🔍 Include:
1. A professional **Resume Score** (out of 100) based on relevance, skills, and structure.
2. A clear list of **Missing or Weak Skills** relevant to this job.
3. Specific **Suggestions to Improve**, focusing on clarity, professionalism, and job alignment.

📝 Resume:
{resume_text}

Make your tone professional, structured, and supportive — like real HR advice.
Avoid generic comments. Base everything strictly on the resume provided.
"""

    response = model.generate_content(prompt)
    return response.text
