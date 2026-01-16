/**
 * Authentication Module
 * Handles login and registration
 */

// Handle registration
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }
        
        try {
            const response = await apiClient.register(name, email, password);
            showMessage('Registration successful! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
}

// Handle login
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await apiClient.login(email, password);
            apiClient.setToken(response.token);
            localStorage.setItem('user', JSON.stringify(response.user));
            
            showMessage('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
}

// Update navbar based on auth status
function updateNavbar() {
    const token = apiClient.getToken();
    const loginLink = document.getElementById('loginLink');
    const logoutLink = document.getElementById('logoutLink');
    
    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'none';
    }
}

// Handle logout
if (document.getElementById('logoutLink')) {
    document.getElementById('logoutLink').addEventListener('click', (e) => {
        e.preventDefault();
        apiClient.clearToken();
        localStorage.removeItem('user');
        updateNavbar();
        window.location.href = 'index.html';
    });
}

// Show message
function showMessage(message, type = 'info') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = type;
        messageEl.style.display = 'block';
    }
}

// Initialize navbar on page load
document.addEventListener('DOMContentLoaded', updateNavbar);
