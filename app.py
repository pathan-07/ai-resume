
import os
import sys

# Add the deploy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume-analyzer', 'deploy'))

# Change to the deploy directory
os.chdir(os.path.join(os.path.dirname(__file__), 'resume-analyzer', 'deploy'))

# Import and run the actual app
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
