import sys
import os

# Add the deploy directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume-analyzer', 'deploy'))

# Import the Flask app
from app import app

# Export the app for Vercel
application = app

if __name__ == "__main__":
    app.run()
