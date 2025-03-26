#!/bin/bash
# Make sure Python 3 is available
python --version || python3 --version

# Install pip if not available
command -v pip || curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py

# Install dependencies
cd backend
pip install -r requirements.txt

echo "Build completed successfully!" 