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

def generate_pdf(html_content):
    """Generates a PDF from HTML content using ReportLab."""
    try:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Remove HTML tags and convert to plain text
        clean_text = re.sub('<.*?>', '', html_content)
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')

        # Split into paragraphs
        paragraphs = clean_text.split('\n')

        for para in paragraphs:
            if para.strip():
                if any(heading in para for heading in ['Resume Analysis', 'Job Role', 'Score', 'Skills']):
                    story.append(Paragraph(para.strip(), styles['Heading2']))
                else:
                    story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def extract_analysis_data(text):
    """Extract structured data from analysis text for visualization."""
    import re
    
    data = {
        'score': 0,
        'strengths': [],
        'improvements': [],
        'missing_skills': [],
        'categories': {
            'technical_skills': 0,
            'experience': 0,
            'education': 0,
            'presentation': 0
        }
    }
    
    # Extract score
    score_match = re.search(r'score.*?(\d+)', text, re.IGNORECASE)
    if score_match:
        data['score'] = int(score_match.group(1))
    
    # Extract sections
    sections = re.split(r'\*\*(.*?)\*\*', text)
    current_section = None
    
    for i, section in enumerate(sections):
        if 'strengths' in section.lower():
            current_section = 'strengths'
        elif 'improvement' in section.lower():
            current_section = 'improvements'
        elif 'missing' in section.lower() or 'skills' in section.lower():
            current_section = 'missing_skills'
        elif current_section and i % 2 == 0:  # Content section
            items = [item.strip() for item in re.split(r'[•\-\*\n]', section) if item.strip()]
            if current_section in data:
                data[current_section].extend(items[:5])  # Limit to 5 items
    
    # Calculate category scores based on content analysis
    score_base = data['score']
    data['categories']['technical_skills'] = min(100, score_base + (10 if 'technical' in text.lower() else -5))
    data['categories']['experience'] = min(100, score_base + (5 if 'experience' in text.lower() else -10))
    data['categories']['education'] = min(100, score_base + (0 if 'education' in text.lower() else -5))
    data['categories']['presentation'] = min(100, score_base + (5 if len(data['strengths']) > 2 else -15))
    
    return data

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