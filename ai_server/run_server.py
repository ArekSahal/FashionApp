#!/usr/bin/env python3
"""
Entry point for the AI server.
Starts the Flask server for outfit search API.
"""

import sys
import os

def main():
    print("🤖 FashionApp AI Server")
    print("=" * 30)
    print("Starting Flask server...")
    print("Server will be available at: http://localhost:5003")
    print("Press Ctrl+C to stop the server")
    print("-" * 30)
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=5003, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 