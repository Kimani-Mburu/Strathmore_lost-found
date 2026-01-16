@echo off
REM Installation and Setup Script for Development (Windows)

echo Setting up Strathmore Digital Lost and Found Application...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r backend\requirements.txt

REM Initialize database
python backend\init_db.py

echo Setup complete!
echo.
echo To start the backend server, run:
echo   venv\Scripts\activate.bat
echo   cd backend
echo   python run.py
echo.
echo Then open frontend\index.html in your browser
pause
