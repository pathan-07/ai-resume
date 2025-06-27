from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from markupsafe import Markup
import sqlite3
import os
import traceback
import io
import re
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from resume_parser import extract_text
from analysis import analyze_resume
from xhtml2pdf import pisa
from email.message import EmailMessage
from email.utils import formataddr
import smtplib

# App and config
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_super_secret_key")  # change to a secure random string
load_dotenv()

DB_PATH = "resume_ai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Email function
def send_email(receiver_email, subject, body, attachment=None):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = EmailMessage()
    msg['From'] = formataddr(("CareerGPT", sender_email))
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.set_content(body)

    if attachment:
        msg.add_attachment(attachment.getvalue(), maintype='application', subtype='pdf', filename="Resume_Report.pdf")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

# PDF generator
def generate_pdf(html):
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf, encoding='utf-8')
    pdf.seek(0)
    return pdf

# Formatting functions
def format_for_web(text):
    text = re.sub(r'(\d+)/100', r'<span class="badge bg-primary fs-6">\1/100</span>', text)
    text = re.sub(r'^(\d+\.\s*[A-Za-z\s]+:?)$', r'<h5 class="mt-4 mb-3 fw-bold">\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^[\-\*]\s*(.*?)$', r'<div class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>\1</div>', text, flags=re.MULTILINE)
    paragraphs = text.split('\n\n')
    result = [f'<p>{p}</p>' if not p.startswith('<h5') and not p.startswith('<div') else p for p in paragraphs if p.strip()]
    return Markup('<div class="analysis-content">' + '\n'.join(result) + '</div>')

# DB helpers
def get_user(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_history(user_id, job_role, result):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO analysis_history (user_id, job_role, result) VALUES (?, ?, ?)", 
                    (user_id, job_role, result))
        conn.commit()
    except Exception as e:
        print(f"Error saving history: {e}")
    finally:
        conn.close()

# Routes
@app.route("/")
def index():
    # Redirect to login page if not logged in
    if "user_id" not in session:
        return redirect(url_for('login'))
    # If logged in, go to the analysis page
    return redirect(url_for('analyze_page'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            conn.close()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            flash("Email already exists.", "danger")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for("analyze_page"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/analyze", methods=["POST"])
def analyze():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    job_role = request.form.get("job_role")
    if not job_role:
        flash("Please specify a job role.", "warning")
        return redirect(url_for("analyze_page"))
    
    # Get email address from form
    recipient_email = request.form.get("email")
    
    if "resume" not in request.files:
        flash("No resume file selected.", "danger")
        return redirect(url_for("analyze_page"))
        
    file = request.files["resume"]
    if not file or file.filename == "":
        flash("No resume file selected.", "danger")
        return redirect(url_for("analyze_page"))

    try:
        resume_text = extract_text(file)
        result = analyze_resume(resume_text, job_role)
        save_history(session["user_id"], job_role, result)

        # Save latest to session for PDF/email
        session["latest_result"] = result
        session["latest_role"] = job_role
        
        # If email was provided, send the report immediately
        if recipient_email:
            html = render_template("report.html", result=format_for_web(result), job_role=job_role, now=datetime.now())
            pdf = generate_pdf(html)
            email_sent = send_email(recipient_email, f"Resume Report for {job_role}", "Find attached your analysis result.", attachment=pdf)
            
            if email_sent:
                flash("Analysis report sent to the provided email successfully!", "success")
            else:
                flash("Failed to send email. Please try again later.", "danger")
        
        flash("Resume analysis completed successfully!", "success")
        return render_template("index.html", result=format_for_web(result), job_role=job_role)
    except Exception as e:
        flash(f"Error analyzing resume: {str(e)}", "danger")
        return redirect(url_for("analyze_page"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC", (session["user_id"],))
    history = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", name=session["user_name"], history=history)

@app.route("/download-pdf")
def download_pdf():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
        
    if "latest_result" not in session:
        flash("No analysis result available to download.", "warning")
        return redirect(url_for("dashboard"))
    
    try:
        html = render_template("report.html", result=format_for_web(session["latest_result"]), job_role=session["latest_role"], now=datetime.now())
        pdf = generate_pdf(html)
        return send_file(pdf, as_attachment=True, download_name="Resume_Analysis.pdf", mimetype="application/pdf")
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for("dashboard"))

@app.route("/email-result")
def email_result():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
        
    if "latest_result" not in session:
        flash("No analysis result available to email.", "warning")
        return redirect(url_for("dashboard"))

    try:
        html = render_template("report.html", result=format_for_web(session["latest_result"]), job_role=session["latest_role"], now=datetime.now())
        pdf = generate_pdf(html)
        email_sent = send_email(session["user_email"], f"Resume Report for {session['latest_role']}", "Find attached your analysis result.", attachment=pdf)

        if email_sent:
            flash("Analysis report sent to your email successfully!", "success")
        else:
            flash("Failed to send email. Please try again later.", "danger")
            
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")
        return redirect(url_for("dashboard"))

@app.route("/email-analysis/<int:analysis_id>")
def email_analysis(analysis_id):
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    
    # Get the specific analysis
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE id = ? AND user_id = ?", 
                  (analysis_id, session["user_id"]))
    analysis = cursor.fetchone()
    conn.close()
    
    if not analysis:
        flash("Analysis not found or you don't have permission to access it.", "danger")
        return redirect(url_for("dashboard"))
    
    try:
        html = render_template("report.html", 
                              result=format_for_web(analysis["result"]), 
                              job_role=analysis["job_role"], 
                              now=datetime.now())
        pdf = generate_pdf(html)
        email_sent = send_email(session["user_email"], 
                               f"Resume Report for {analysis['job_role']}", 
                               "Find attached your analysis result.", 
                               attachment=pdf)

        if email_sent:
            flash("Analysis report sent to your email successfully!", "success")
        else:
            flash("Failed to send email. Please try again later.", "danger")
            
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Error sending email: {str(e)}", "danger")
        return redirect(url_for("dashboard"))

@app.route("/analyze-page")
def analyze_page():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
