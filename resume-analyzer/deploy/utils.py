import os
import io
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import weasyprint
from dotenv import load_dotenv

load_dotenv()

def send_email(receiver_email, subject, body, attachment=None):
    # (Is function me koi badlav nahi hai)
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("SENDER_EMAIL and SENDER_PASSWORD environment variables are required.")
        return False

    msg = EmailMessage()
    msg['From'] = formataddr(("Resume Analyzer", sender_email))
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
        print(f"Error sending email: {e}")
        return False

def generate_pdf(html_string):
    """HTML se PDF generate karta hai using weasyprint."""
    try:
        # Create PDF from HTML string
        pdf_buffer = io.BytesIO()
        
        # WeasyPrint ke saath PDF generate karein
        html_doc = weasyprint.HTML(string=html_string, base_url=os.path.dirname(__file__))
        pdf_doc = html_doc.write_pdf()
        
        # PDF content ko buffer mein write karein
        pdf_buffer.write(pdf_doc)
        pdf_buffer.seek(0)
        return pdf_buffer
        
    except Exception as e:
        print(f"An unexpected error occurred in generate_pdf: {e}")
        return None

def format_for_web(text):
    # (Is function me koi badlav nahi hai)
    if not text:
        return '<div class="analysis-content"><p>No analysis data available.</p></div>'
    # ... baaki ka code waisa hi rahega
    text = text.strip()
    text = re.sub(r'\*\*(Resume Score.*?)\*\*', r'<h5><i class="fas fa-star"></i> \1</h5>', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(Strengths.*?)\*\*', r'<h5><i class="fas fa-thumbs-up"></i> \1</h5>', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(Areas for Improvement.*?)\*\*', r'<h5><i class="fas fa-lightbulb"></i> \1</h5>', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(Missing Skills.*?)\*\*', r'<h5><i class="fas fa-exclamation-triangle"></i> \1</h5>', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<h5><i class="fas fa-info-circle"></i> \1</h5>', text)
    text = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    formatted_lines = []
    in_section = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_section:
                formatted_lines.append('</div>')
                in_section = False
            continue
        if line.startswith('<h5>'):
            if in_section:
                formatted_lines.append('</div>')
            formatted_lines.append(line)
            formatted_lines.append('<div class="highlight-box">')
            in_section = True
        elif line.startswith(('•', '-', '*')):
            bullet_content = line[1:].strip()
            formatted_lines.append(f'<div class="info-box"><i class="fas fa-check-circle"></i> {bullet_content}</div>')
        else:
            if not in_section:
                formatted_lines.append('<div class="highlight-box">')
                in_section = True
            formatted_lines.append(f'<p>{line}</p>')
    if in_section:
        formatted_lines.append('</div>')
    return '<div class="analysis-content">' + '\n'.join(formatted_lines) + '</div>'
