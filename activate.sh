#!/bin/bash
# Quick activation script for the virtual environment (Linux/Mac)

echo "Activating Stock Market Analysis Tool environment..."
source venv/bin/activate

echo ""
echo "========================================"
echo "Virtual Environment Activated!"
echo "========================================"
echo ""
echo "Available commands:"
echo "  python main.py          - Run the main application"
echo "  python test_setup.py    - Test the installation"
echo "  deactivate              - Exit virtual environment"
echo ""
echo "Current Python: $(pwd)/venv/bin/python"
echo ""

# Start a new shell with the environment activated
$SHELL
