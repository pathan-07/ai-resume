import os
import io
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from dotenv import load_dotenv
import re
from html import unescape

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

def clean_html_for_pdf(html_string):
    """HTML content ko clean text mein convert karta hai PDF ke liye."""
    # Remove HTML tags
    clean_text = re.sub('<[^<]+?>', '', html_string)
    # Decode HTML entities
    clean_text = unescape(clean_text)
    # Clean up extra whitespace
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    clean_text = re.sub(r' +', ' ', clean_text)
    return clean_text.strip()

def generate_pdf(html_string):
    """HTML se PDF generate karta hai using reportlab."""
    try:
        pdf_buffer = io.BytesIO()
        
        # HTML content ko clean text mein convert karein
        clean_text = clean_html_for_pdf(html_string)
        
        # ReportLab ke saath PDF generate karein
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor='#4f46e5'
        )
        
        # Normal style
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leftIndent=0,
            rightIndent=0
        )
        
        # Split content into paragraphs
        paragraphs = clean_text.split('\n')
        
        for para in paragraphs:
            if para.strip():
                if 'Resume Analysis Report' in para:
                    story.append(Paragraph(para.strip(), title_style))
                else:
                    story.append(Paragraph(para.strip(), normal_style))
                story.append(Spacer(1, 6))
        
        doc.build(story)
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
