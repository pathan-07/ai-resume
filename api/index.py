import sys
import os

# Add the resume-analyzer/deploy directory to the Python path
current_dir = os.path.dirname(__file__)
app_dir = os.path.join(current_dir, '..', 'resume-analyzer', 'deploy')
sys.path.insert(0, app_dir)

# Change working directory to the app directory
os.chdir(app_dir)

# Import the Flask app
from app import app

# For Vercel, we need to export the app object
# Vercel will automatically detect this as the WSGI application
app = app
