from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Hello Flask from Ankit Reddy!",
        "MONGODB_URI_present": bool(os.getenv("MONGODB_URI"))
    })

if __name__ == "__main__":
    import sys
    port = 5000
    # Allow: python flask_app/app.py --port 5050
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    app.run(debug=True, port=port)