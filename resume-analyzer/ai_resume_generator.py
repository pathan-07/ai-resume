import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

def initialize_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is not set.")
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Error initializing Google Generative AI: {e}")
        return None

model = initialize_genai()

def generate_ai_resume(user_input):
    if not model:
        raise Exception("AI model is not initialized. Please check the API key.")

    # Data ko prompt ke liye prepare karein
    experience_str = ""
    if isinstance(user_input.get('experience'), list):
        for exp in user_input['experience']:
            achievements = "\n".join([f"- {ach}" for ach in exp['achievements']])
            experience_str += f"\nTitle: {exp['title']}\nCompany: {exp['company']}\nDates: {exp['dates']}\nAchievements:\n{achievements}\n"
    else:
        experience_str = user_input.get('experience', 'N/A')

    education_str = ""
    if isinstance(user_input.get('education'), list):
         for edu in user_input['education']:
             education_str += f"\nDegree: {edu['degree']}\nInstitution: {edu['institution']}\nYear: {edu['year']}\n"
    else:
        education_str = user_input.get('education', 'N/A')

    prompt = f"""
    You are an expert career coach and professional resume writer. Based on the user's provided information, generate a complete, professional, and ATS-friendly resume.
    The final output MUST be a single, valid JSON object. Do not include any text, notes, or markdown formatting outside of the JSON object.

    **User's Information:**
    - Name: {user_input.get('name', 'N/A')}
    - Email: {user_input.get('email', 'N/A')}
    - Phone: {user_input.get('phone', 'N/A')}
    - Target Job Role: {user_input.get('job_role', 'N/A')}
    - Provided Skills: {user_input.get('skills', 'N/A')}
    - Provided Experience: {experience_str.strip()}
    - Provided Education: {education_str.strip()}

    **Your Task:**
    1.  **Professional Summary:** Write a compelling 3-4 sentence summary tailored to the target job role.
    2.  **Skills:** Expand the user's skills into a categorized list (Technical, Soft Skills, Tools).
    3.  **Experience:** Convert the provided experience into a professional format. Ensure each role has 3-5 achievement-oriented bullet points. If the user provided bullet points, refine them. If they provided a paragraph, extract achievements and write them in the STAR method.
    4.  **Education:** Format the education details professionally.

    **JSON Output Structure:**
    {{
      "name": "{user_input.get('name')}",
      "email": "{user_input.get('email')}",
      "phone": "{user_input.get('phone')}",
      "job_role": "{user_input.get('job_role')}",
      "summary": "...",
      "skills": {{ "Technical": [...], "Soft Skills": [...], "Tools": [...] }},
      "experience": [ {{ "title": "...", "company": "...", "dates": "...", "achievements": [...] }} ],
      "education": [ {{ "degree": "...", "institution": "...", "year": "..." }} ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response.text)
        json_str = json_match.group(1) if json_match else response.text
        resume_data = json.loads(json_str)
        return resume_data
    except Exception as e:
        print(f"Error generating or parsing AI resume: {e}")
        # Graceful fallback
        return {
            'name': user_input.get('name'), 'email': user_input.get('email'), 'phone': user_input.get('phone'),
            'job_role': user_input.get('job_role'), 'summary': "Sorry, the AI could not generate a resume at this time. Please try again.",
            'skills': {{"Error": ["Could not generate skills."]}}, 'experience': [], 'education': []
        }

