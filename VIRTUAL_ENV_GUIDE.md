# Python Virtual Environment Setup Guide

This guide covers different ways to set up a Python virtual environment for the Indian Stock Market Analysis Tool.

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script
```bash
# Run the automated setup script
python setup.py
```

### Option 2: Platform-specific Scripts
**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

## 📋 Manual Setup Options

### 1. **venv** (Built-in - Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### 2. **conda** (Anaconda/Miniconda)
```bash
# Create environment
conda create -n stockmarket python=3.9

# Activate
conda activate stockmarket

# Install dependencies
pip install -r requirements.txt

# Deactivate
conda deactivate
```

### 3. **virtualenv** (Third-party)
```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. **pipenv** (Modern approach)
```bash
# Install pipenv
pip install pipenv

# Create Pipfile and install dependencies
pipenv install -r requirements.txt

# Activate shell
pipenv shell

# Or run commands directly
pipenv run python main.py
```

### 5. **poetry** (Advanced dependency management)
```bash
# Install poetry
pip install poetry

# Initialize project (if starting fresh)
poetry init

# Add dependencies
poetry add yfinance pandas numpy

# Install dependencies
poetry install

# Activate shell
poetry shell

# Or run commands
poetry run python main.py
```

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. Python not found:**
```bash
# Check Python installation
python --version
# or
python3 --version

# Add Python to PATH (Windows)
# Go to System Properties > Environment Variables > Add Python installation directory
```

**2. pip not working:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Use python -m pip instead of pip
python -m pip install package_name
```

**3. Permission errors (Linux/Mac):**
```bash
# Don't use sudo with pip in virtual environments
# If needed, fix permissions:
sudo chown -R $USER:$USER /path/to/project
```

**4. Package installation fails:**
```bash
# Try minimal requirements first
pip install -r requirements-minimal.txt

# Install packages individually
pip install yfinance pandas numpy
```

## 📊 Virtual Environment Comparison

| Tool | Pros | Cons | Best For |
|------|------|------|----------|
| **venv** | Built-in, simple, reliable | Basic features only | General use, beginners |
| **conda** | Manages Python versions, scientific packages | Large download, complex | Data science, multiple Python versions |
| **virtualenv** | More features than venv | Requires installation | Advanced features |
| **pipenv** | Modern, Pipfile, automatic activation | Learning curve | Modern Python development |
| **poetry** | Advanced dependency management, packaging | Complex setup | Professional development |

## 🎯 Recommended Approach

For this stock market analysis tool, we recommend:

1. **Beginners**: Use `venv` (built-in)
2. **Data Scientists**: Use `conda`
3. **Modern Developers**: Use `pipenv` or `poetry`

## ⚡ Quick Start Commands

After setting up your virtual environment:

```bash
# Test the setup
python test_setup.py

# Run the application
python main.py

# For development
python -c "from src.core.strategies.intraday_strategy import IntradayStrategy; print('✓ Setup working!')"
```

## 🔍 Environment Verification

To verify your environment is working:

```python
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

# Check if virtual environment is active
import os
if 'VIRTUAL_ENV' in os.environ:
    print("✓ Virtual environment active:", os.environ['VIRTUAL_ENV'])
else:
    print("⚠️ Virtual environment not detected")
```

## 📝 Environment Management Tips

1. **Always activate your environment** before working on the project
2. **Keep requirements.txt updated** when adding new packages
3. **Don't commit the virtual environment** to version control
4. **Use different environments** for different projects
5. **Document your setup** for team members

Choose the method that best fits your workflow and experience level!
