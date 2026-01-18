"""
Test runner script for the Lost & Found application
"""

import os
import sys
import subprocess

def run_tests():
    """Run the test suite"""
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("Installing pytest and dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-flask', 'pytest-cov'])
    
    # Run tests
    print("Running test suite...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        'tests/'
    ])
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())