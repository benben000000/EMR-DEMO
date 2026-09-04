#!/usr/bin/env python3
"""
G1 Health EMR - Vercel Serverless Function & API Handler
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud
"""

import os
import sys

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


if __name__ == "__main__":
    from serve_demo import run_server
    run_server()
