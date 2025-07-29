import PyPDF2
import docx
import io

def extract_text(file):
    """
    Extracts text from a file (PDF or DOCX).
    """
    filename = file.filename
    try:
        if filename.endswith(".pdf"):
            # For PDF files, we read the content into a BytesIO object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif filename.endswith(".docx"):
            # For DOCX files, we can directly read the file
            doc = docx.Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        else:
            return "Error: Unsupported file type. Please upload a PDF or DOCX file."
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return f"Error processing file: {e}"