#!/usr/bin/env python3
"""
Startup script for the Chess Opening Recommendation API.
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting Chess Opening Recommendation API...")
    print(f"📡 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"📖 ReDoc Documentation: http://{host}:{port}/redoc")
    print(f"🔍 OpenAPI Spec: http://{host}:{port}/openapi.json")
    print(f"💚 Health Check: http://{host}:{port}/health")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        log_level="info",
        workers=2
    ) 