#!/usr/bin/env python3
"""
Flask web UI for local translator.
Supports Korean <-> English translation with web interface.
"""
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.translator import Translator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Enable Korean characters in JSON

# Global translator instance
translator = None


def detect_language(text: str) -> str:
    """
    Simple language detection based on character analysis.
    Returns 'ko' for Korean, 'en' for English.
    """
    korean_chars = sum(1 for char in text if '\uac00' <= char <= '\ud7a3')
    total_chars = len([char for char in text if char.strip()])

    if total_chars == 0:
        return 'en'

    korean_ratio = korean_chars / total_chars
    return 'ko' if korean_ratio > 0.3 else 'en'


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Translation API endpoint.

    Request JSON:
        {
            "text": "Text to translate",
            "src_lang": "en",  # Optional, auto-detect if not provided
            "tgt_lang": "ko",  # Optional, auto-detect if not provided
            "auto_detect": true  # Optional, default: true
        }

    Response JSON:
        {
            "success": true,
            "translation": "Translated text",
            "detected_lang": "en",
            "src_lang": "en",
            "tgt_lang": "ko"
        }
    """
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        text = data['text'].strip()

        if not text:
            return jsonify({
                'success': False,
                'error': 'Empty text'
            }), 400

        # Get parameters
        auto_detect = data.get('auto_detect', True)
        src_lang = data.get('src_lang', 'en')
        tgt_lang = data.get('tgt_lang', 'ko')

        # Auto-detect language if enabled
        detected_lang = None
        if auto_detect:
            detected_lang = detect_language(text)
            if detected_lang == 'ko':
                src_lang, tgt_lang = 'ko', 'en'
            else:
                src_lang, tgt_lang = 'en', 'ko'

        # Perform translation
        logger.info(f"Translating from {src_lang} to {tgt_lang}")
        translation = translator.translate(text, src_lang=src_lang, tgt_lang=tgt_lang)

        return jsonify({
            'success': True,
            'translation': translation,
            'detected_lang': detected_lang,
            'src_lang': src_lang,
            'tgt_lang': tgt_lang
        })

    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/supported_languages', methods=['GET'])
def supported_languages():
    """
    Get supported languages.

    Response JSON:
        {
            "success": true,
            "languages": {
                "en": "eng_Latn",
                "ko": "kor_Hang",
                ...
            }
        }
    """
    try:
        languages = translator.get_supported_languages()
        return jsonify({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'translator_loaded': translator is not None
    })


def main():
    """Main function to run the Flask app."""
    global translator

    import argparse
    parser = argparse.ArgumentParser(description='Flask Web UI for Local Translator')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to bind to (default: 5000)')
    parser.add_argument('--no-gpu', action='store_true',
                        help='Disable GPU usage')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')

    args = parser.parse_args()

    # Initialize translator
    logger.info("Initializing translator... This may take a minute.")
    try:
        translator = Translator(use_gpu=not args.no_gpu)
        logger.info("Translator initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize translator: {e}")
        sys.exit(1)

    # Run Flask app
    logger.info(f"Starting Flask server on http://{args.host}:{args.port}")
    logger.info("Press Ctrl+C to stop the server")

    if args.host == '0.0.0.0':
        logger.info(f"Access the web UI from your local browser using SSH port forwarding:")
        logger.info(f"  ssh -L {args.port}:localhost:{args.port} user@your-server")
        logger.info(f"  Then open: http://localhost:{args.port}")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
