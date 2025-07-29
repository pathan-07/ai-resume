import os
import io
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from xhtml2pdf import pisa  # WeasyPrint ki jagah iska istemal hoga
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
    """HTML se PDF generate karta hai using xhtml2pdf, handling local paths correctly."""
    pdf_buffer = io.BytesIO()
    
    # Define a link callback to resolve local file paths
    def link_callback(uri, rel):
        # Use os.path.join to handle file paths correctly across operating systems
        # The base path should be the 'static' folder in your project directory
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        path = os.path.join(static_path, uri.replace("/", os.sep))

        # Ensure the file exists
        if not os.path.isfile(path):
            # Fallback for other potential paths if needed, or return original uri
            return uri
        return path

    try:
        pisa_status = pisa.CreatePDF(
            io.StringIO(html_string),  # source HTML
            dest=pdf_buffer,           # destination PDF
            link_callback=link_callback # custom function to resolve paths
        )
        
        if pisa_status.err:
            print('Error generating PDF:', pisa_status.err)
            return None
            
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
