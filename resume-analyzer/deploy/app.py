from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import io

# Local Imports
from models import db, User, ResumeAnalysis
from utils import send_email, generate_pdf, format_for_web
from resume_parser import extract_text
from analysis import analyze_resume
from ai_resume_generator import generate_ai_resume

# App and Config
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "a-very-secure-and-random-string-that-is-hard-to-guess")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'resume_ai.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# --- Routes ---

@app.route("/")
def index():
    if "user_id" not in session:
        return render_template('welcome.html')
    return redirect(url_for('analyze_page'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([name, email, password]):
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("signup.html")

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash("Login successful!", "success")
            return redirect(url_for("analyze_page"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/analyze_page")
def analyze_page():
    if "user_id" not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

def save_history(user_id, job_role, result):
    """Saves the analysis result to the database."""
    new_analysis = ResumeAnalysis(user_id=user_id, job_role=job_role, result=result)
    db.session.add(new_analysis)
    db.session.commit()

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == 'GET':
        return redirect(url_for('analyze_page'))

    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    job_role = request.form.get("job_role")
    if not job_role:
        flash("Job role is required.", "warning")
        return redirect(url_for("analyze_page"))

    recipient_email = request.form.get("email")

    if "resume" not in request.files:
        flash("Resume file not selected.", "danger")
        return redirect(url_for("analyze_page"))

    file = request.files["resume"]
    if not file or file.filename == "":
        flash("Resume file not selected.", "danger")
        return redirect(url_for("analyze_page"))

    try:
        resume_text = extract_text(file)
        if "Error" in resume_text:
             flash(resume_text, "danger")
             return redirect(url_for("analyze_page"))

        result = analyze_resume(resume_text, job_role)
        save_history(session["user_id"], job_role, result)

        session["latest_result"] = result
        session["latest_role"] = job_role

        if recipient_email:
            html = render_template("report.html", result=format_for_web(result), job_role=job_role, now=datetime.now())
            pdf = generate_pdf(html)
            if pdf:
                email_sent = send_email(recipient_email, f"Resume Report for {job_role}", "Your analysis result is attached.", attachment=pdf)
                if email_sent:
                    flash("Analysis report has been sent to your email!", "success")
                else:
                    flash("Could not send email. Please try again later.", "danger")
            else:
                flash("Could not generate PDF for email.", "danger")

        flash("Resume analysis completed successfully!", "success")
        return render_template("index.html", result=format_for_web(result), job_role=job_role)
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for("analyze_page"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    history = ResumeAnalysis.query.filter_by(user_id=session["user_id"]).order_by(ResumeAnalysis.created_at.desc()).all()
    return render_template("dashboard.html", name=session.get("user_name"), history=history)

@app.route("/download_pdf")
def download_pdf():
    if "user_id" not in session or "latest_result" not in session:
        flash("No analysis result available to download.", "warning")
        return redirect(url_for("dashboard"))

    html = render_template("report.html", result=format_for_web(session["latest_result"]), job_role=session["latest_role"], now=datetime.now())
    pdf = generate_pdf(html)
    if pdf:
        return send_file(pdf, as_attachment=True, download_name="Resume_Analysis.pdf", mimetype="application/pdf")
    else:
        flash("Error generating PDF.", "danger")
        return redirect(url_for("dashboard"))

@app.route("/email-result")
def email_result():
    """Emails the most recent analysis result from the session."""
    if "user_id" not in session or "latest_result" not in session:
        flash("No recent analysis available to email.", "warning")
        return redirect(url_for("dashboard"))

    try:
        html = render_template("report.html", result=format_for_web(session["latest_result"]), job_role=session["latest_role"], now=datetime.now())
        pdf = generate_pdf(html)
        if pdf and send_email(session["user_email"], f"Resume Report for {session['latest_role']}", "Find your analysis attached.", attachment=pdf):
            flash("Analysis report sent to your email!", "success")
        else:
            flash("Failed to send email.", "danger")
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")

    return redirect(url_for("dashboard"))


@app.route("/email-analysis/<int:analysis_id>")
def email_analysis(analysis_id):
    """Emails a specific analysis from the user's history."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    analysis = db.session.get(ResumeAnalysis, analysis_id)
    if not analysis or analysis.user_id != session["user_id"]:
        flash("Analysis not found or you don't have permission.", "danger")
        return redirect(url_for("dashboard"))

    try:
        html = render_template("report.html", result=format_for_web(analysis.result), job_role=analysis.job_role, now=datetime.now())
        pdf = generate_pdf(html)
        if pdf and send_email(session["user_email"], f"Resume Report for {analysis.job_role}", "Find your analysis attached.", attachment=pdf):
            flash("Analysis report sent to your email!", "success")
        else:
            flash("Failed to send email.", "danger")
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")

    return redirect(url_for("dashboard"))

@app.route("/build-resume", methods=["GET", "POST"])
def build_resume():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        session['generated_resume'] = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'job_role': request.form.get('job_role'),
            'skills': [skill.strip() for skill in request.form.get('skills', '').split(',')],
            'education': request.form.get('education'),
            'experience': request.form.get('experience'),
            'certifications': request.form.get('certifications'),
            'achievements': request.form.get('achievements')
        }
        return render_template("resume_result.html", resume_data=session['generated_resume'])

    return render_template("build_resume.html")

@app.route("/ai-resume-builder", methods=["GET", "POST"])
def ai_resume_builder():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        user_input = {k: v for k, v in request.form.items()}
        
        # Check karein ki experience aur education me sufficient details hain ya nahi
        # Hum 50 characters ka threshold rakhte hain
        if len(user_input.get('experience', '')) < 50 or len(user_input.get('education', '')) < 20:
            flash("For a better result, please provide more specific details.", "info")
            # User ko detailed form par redirect karein
            return render_template("ai_builder_details.html", user_input=user_input)
        
        # Agar details sufficient hain, to direct resume generate karein
        try:
            ai_resume = generate_ai_resume(user_input)
            session['generated_resume'] = ai_resume
            flash("Your professional resume has been generated by AI!", "success")
            return render_template("resume_result.html", resume_data=ai_resume, ai_generated=True)
        except Exception as e:
            flash(f"Error generating AI resume: {str(e)}", "danger")
            return redirect(url_for("ai_resume_builder"))

    return render_template("ai_resume_builder.html")

@app.route("/ai-generate-detailed", methods=["POST"])
def ai_generate_detailed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Detailed form se saara data collect karein
    user_input = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'job_role': request.form.get('job_role'),
        'skills': request.form.get('skills'),
        'experience': [],
        'education': []
    }

    # Dynamic experience entries ko parse karein
    exp_index = 0
    while f'exp-title-{exp_index}' in request.form:
        achievements = request.form.get(f'exp-achievements-{exp_index}', '').strip().split('\n')
        user_input['experience'].append({
            'title': request.form.get(f'exp-title-{exp_index}'),
            'company': request.form.get(f'exp-company-{exp_index}'),
            'dates': request.form.get(f'exp-dates-{exp_index}'),
            'achievements': [ach.strip() for ach in achievements if ach.strip()]
        })
        exp_index += 1

    # Dynamic education entries ko parse karein
    edu_index = 0
    while f'edu-degree-{edu_index}' in request.form:
        user_input['education'].append({
            'degree': request.form.get(f'edu-degree-{edu_index}'),
            'institution': request.form.get(f'edu-institution-{edu_index}'),
            'year': request.form.get(f'edu-year-{edu_index}')
        })
        edu_index += 1
    
    # Ab is structured data se resume generate karein
    try:
        ai_resume = generate_ai_resume(user_input)
        session['generated_resume'] = ai_resume
        flash("Your professional resume has been generated by AI with your detailed input!", "success")
        return render_template("resume_result.html", resume_data=ai_resume, ai_generated=True)
    except Exception as e:
        flash(f"Error generating detailed AI resume: {str(e)}", "danger")
        return redirect(url_for("ai_resume_builder"))

@app.route("/download-resume-pdf")
def download_resume_pdf():
    if "user_id" not in session or "generated_resume" not in session:
        flash("No resume data available to download.", "warning")
        return redirect(url_for("build_resume"))

    resume_data = session.get("generated_resume")
    try:
        # HTML template render karein
        html_string = render_template("resume_pdf.html", resume_data=resume_data)
        
        # Hamare universal generate_pdf function ka istemal karein
        pdf_file = generate_pdf(html_string)
        
        if pdf_file:
            return send_file(
                pdf_file,
                as_attachment=True,
                download_name=f"{resume_data.get('name', 'Resume').replace(' ', '_')}_Resume.pdf",
                mimetype="application/pdf"
            )
        else:
            flash("Error generating PDF.", "danger")
            return redirect(url_for("build_resume"))
            
    except Exception as e:
        flash(f"An unexpected error occurred while generating PDF: {str(e)}", "danger")
        return redirect(url_for("build_resume"))

if __name__ == "__main__":
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Folder already exists

    with app.app_context():
        db.create_all()

    # Use PORT environment variable for production, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    # Disable debug mode for production
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)