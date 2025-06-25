#!/usr/bin/env python3
"""
FashionApp AI Server Runner

This script starts the Flask server for the FashionApp AI service.
"""

import os
from app import app

def main():
    """Start the Flask server"""
    try:
        # Get port from environment variable (Railway provides this)
        port = int(os.environ.get('PORT', 5003))
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass

if __name__ == "__main__":
    main() 