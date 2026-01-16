# Contributing to Strathmore Lost & Found

Thank you for your interest in contributing to the Strathmore University Digital Lost & Found Web Application!

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button at the top right of the repository.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/lostnfound.git
cd lostnfound
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes
- Write clean, readable code
- Follow PEP 8 style guide for Python
- Use meaningful variable and function names
- Add comments for complex logic

### 5. Test Your Changes
```bash
cd backend
python -m pytest
# or
python test_api.py
```

### 6. Commit Your Changes
```bash
git add .
git commit -m "Add your descriptive commit message"
```

### 7. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request
Go to the original repository and click "New Pull Request". Select your fork and branch.

## Code Standards

### Python
- Use PEP 8 formatting
- Maximum line length: 100 characters
- Use type hints where possible
- Write docstrings for functions and classes

### JavaScript
- Use camelCase for variables and functions
- Use const/let instead of var
- Write comments for complex logic
- Validate user input

### HTML/CSS
- Use semantic HTML
- Avoid inline styles
- Follow BEM naming convention for CSS classes
- Ensure responsive design

## Commit Message Format

```
[TYPE] Brief description

Longer description explaining the changes if needed.

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat: Add email notifications for new items`
- `fix: Resolve login redirect issue`
- `docs: Update API documentation`

## Reporting Issues

### Security Issues
DO NOT open a public issue for security vulnerabilities. Email security concerns to the development team.

### Bug Reports
Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Browser/Python version

### Feature Requests
Include:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach

## Development Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the application
python run.py
```

## Project Structure Overview

```
backend/
├── app/
│   ├── models/        # Database models
│   ├── routes/        # API endpoints
│   ├── utils/         # Helper functions
│   └── static/        # Frontend files
├── run.py             # Entry point
├── requirements.txt   # Dependencies
└── test_api.py        # API tests
```

## Key Points

- Always work on a feature branch
- Keep commits focused and atomic
- Write descriptive commit messages
- Test your code before submitting PR
- Update documentation as needed
- Ensure no sensitive data in commits

## Questions?

Feel free to open an issue with the "question" label or contact the development team.

Thank you for contributing! 🎉
