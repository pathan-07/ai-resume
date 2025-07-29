# Resume Analyzer

A modern web application that uses AI to analyze resumes against job descriptions, provide professional feedback, and offer improvement suggestions.

![Resume Analyzer Screenshot](https://example.com/screenshot.png)

## 🚀 Features

- **AI-Powered Resume Analysis**: Uses Google's Gemini AI to provide professional HR-style feedback
- **Skill Matching**: Automatically identifies matched and missing skills based on the selected job role
- **AI Resume Builder**: Generate professional resumes using Google's Gemini AI model
- **PDF Reports**: Generate and download detailed analysis reports
- **Email Delivery**: Send analysis reports directly to your email
- **User Authentication**: Secure signup and login system
- **Analysis History**: Keep track of all your previous resume analyses

## 📋 Requirements

- Python 3.8+
- Flask
- SQLite3
- Google Gemini API Key
- SMTP credentials for email delivery

## 🔧 Installation

1. Clone this repository:
   ```
   git clone https://github.com/pathan-07/resume-analyzer.git
   cd resume-analyzer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root with the following variables:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_AI_API_KEY=your_gemini_api_key
   SECRET_KEY=your_secure_random_string
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_email_app_password
   ```

   To get your Google Gemini API key:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into your `.env` file as both GOOGLE_API_KEY and GOOGLE_AI_API_KEY

6. Initialize the database:
   ```
   python init_db.py
   ```

7. Create an admin user (optional):
   ```
   python create_admin.py
   ```

## 🏃‍♂️ Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## 📝 How to Use

1. Sign up for a new account or log in to an existing one
2. Enter your target job role (e.g., "Data Scientist", "Software Engineer")
3. Upload your resume in PDF format
4. Optionally provide an email address to receive the analysis report
5. Click "Analyze My Resume"
6. Review the detailed feedback, including:
   - Professional HR assessment
   - Resume score
   - Matched and missing skills
   - Improvement suggestions
7. Download the analysis as a PDF or email it for future reference

## 🧰 Supported Job Roles

The application includes skill databases for various tech roles including:

- Software Engineer
- Data Scientist
- Frontend Developer
- Backend Developer
- Full Stack Developer
- DevOps Engineer
- AI Engineer
- Cloud Engineer
- Security Engineer
- UI/UX Designer
- Product Manager
- Digital Marketer
- Blockchain Developer
- AR/VR Developer
- IoT Engineer

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google Generative AI](https://ai.google.dev/) for providing the Gemini API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components
