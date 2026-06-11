from dotenv import load_dotenv
import os
import sys

# ── Ensure backend/ is on the Python path when run from project root ──────────
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# Load .env before anything else touches os.environ
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(debug=debug, host='0.0.0.0')
