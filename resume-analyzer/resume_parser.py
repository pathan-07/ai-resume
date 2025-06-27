import sys
import traceback

print("Importing PyPDF2 in resume_parser.py...")
try:
    import PyPDF2
    print("PyPDF2 imported successfully")
except Exception as e:
    print(f"Error importing PyPDF2: {str(e)}", file=sys.stderr)
    traceback.print_exc()
    raise

# We'll skip docx import for now since it's causing issues
print("NOTE: Skipping docx import - DOCX files will not be supported")

def extract_text(file):
    print(f"Extracting text from file: {file.filename}")
    try:
        if file.filename.endswith(".pdf"):
            print("Processing PDF file...")
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            print(f"Successfully extracted {len(text)} characters from PDF")
            return text
        else:
            print(f"Unsupported file type: {file.filename}")
            return "Only PDF files are supported at this time."
    except Exception as e:
        print(f"Error extracting text: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return f"Error extracting text: {str(e)}"
