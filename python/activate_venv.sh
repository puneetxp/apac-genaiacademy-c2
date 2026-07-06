#!/bin/bash
# Quick activation script for the virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo "Python version: $(python --version)"
echo ""
echo "To start the backend:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
