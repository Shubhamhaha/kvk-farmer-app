from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes.report import report_bp
from routes.chatbot import chatbot_bp
from routes.data import data_bp

# Load backend/.env when running locally; container deployments use environment variables.
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kvk-farmer-secret-2024')

# Register blueprints
app.register_blueprint(report_bp, url_prefix='/api/report')
app.register_blueprint(chatbot_bp, url_prefix='/api/chat')
app.register_blueprint(data_bp, url_prefix='/api/data')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'KVK Farmer App Backend Running'})

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0').strip().lower() in {'1', 'true', 'yes'}
    port = int(os.environ.get('PORT', '5000'))
    app.run(debug=debug, port=port, use_reloader=False)
