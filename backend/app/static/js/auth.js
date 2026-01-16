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
                window.location.href = '/login';
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
            console.log('Login response:', response);
            
            if (!response.token || !response.user) {
                throw new Error('Invalid response from server');
            }
            
            apiClient.setToken(response.token);
            localStorage.setItem('user', JSON.stringify(response.user));
            console.log('Token stored:', apiClient.getToken());
            console.log('User stored:', localStorage.getItem('user'));
            
            // Determine where to redirect based on user role
            let redirectUrl = '/my-dashboard';
            if (response.user.role === 'admin') {
                redirectUrl = '/admin-dashboard';
            }
            
            console.log('Login successful, user role:', response.user.role);
            console.log('Redirecting to:', redirectUrl);
            showMessage('Login successful! Redirecting...', 'success');
            
            // Use multiple redirect methods for safety
            setTimeout(() => {
                console.log('Attempting redirect to:', redirectUrl);
                window.location.href = redirectUrl;
            }, 500);
        } catch (error) {
            console.error('Login error:', error);
            showMessage(error.message || 'Login failed', 'error');
        }
    });
}

// Update navbar based on auth status
function updateNavbar() {
    const token = apiClient.getToken();
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const reportLink = document.getElementById('reportLink');
    const logoutLink = document.getElementById('logoutLink');
    
    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (reportLink) reportLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (reportLink) reportLink.style.display = 'none';
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
        window.location.href = '/';
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
