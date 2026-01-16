/**
 * Main Application Module
 * Handles general app initialization and home page
 */

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    updateNavbar();
});

function initializeApp() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const app = document.getElementById('app');
    
    if (app && Object.keys(user).length > 0) {
        displayDashboard(user);
    } else if (app) {
        displayLandingPage();
    }
}

function displayDashboard(user) {
    const app = document.getElementById('app');
    if (!app) return;
    
    // Add homepage class for background
    document.body.classList.remove('homepage');
    
    app.innerHTML = `
        <div class="container">
            <h2>Welcome, ${user.name}! 👋</h2>
            <div class="dashboard">
                <div class="dashboard-card">
                    <h3>📋 Quick Actions</h3>
                    <ul>
                        <li><a href="/report" class="btn btn-primary">📸 Report Lost/Found Item</a></li>
                        <li><a href="/browse" class="btn btn-secondary" style="margin-top: 0.5rem;">🔍 Browse Items</a></li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function displayLandingPage() {
    const app = document.getElementById('app');
    if (!app) return;
    
    // Add homepage class for background
    document.body.classList.add('homepage');
    
    app.innerHTML = `
        <div class="hero-section">
            <h2>Strathmore University</h2>
            <h2>Lost & Found System</h2>
            <p>Help reunite lost items with their owners on campus</p>
            <div class="hero-buttons">
                <a href="/browse" class="btn btn-primary">🔍 Browse Items</a>
                <a href="/register" class="btn btn-secondary">📝 Get Started</a>
            </div>
        </div>
        
        <div class="container">
            <div class="features-section">
                <div class="feature-card">
                    <h3>📱 Easy to Use</h3>
                    <p>Report lost or found items with photos in just a few clicks.</p>
                </div>
                <div class="feature-card">
                    <h3>🔍 Quick Search</h3>
                    <p>Browse and filter items by category, date, and location.</p>
                </div>
                <div class="feature-card">
                    <h3>✅ Verified Items</h3>
                    <p>All items are verified by admins to ensure authenticity.</p>
                </div>
            </div>
        </div>
    `;
}

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
