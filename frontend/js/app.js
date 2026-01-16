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
    
    app.innerHTML = `
        <div class="container">
            <h2>Welcome, ${user.name}!</h2>
            <div class="dashboard">
                <div class="dashboard-card">
                    <h3>Quick Actions</h3>
                    <ul>
                        <li><a href="report.html" class="btn btn-primary">Report Lost/Found Item</a></li>
                        <li><a href="browse.html" class="btn btn-secondary">Browse Items</a></li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function displayLandingPage() {
    const app = document.getElementById('app');
    if (!app) return;
    
    app.innerHTML = `
        <div class="container">
            <div style="text-align: center; padding: 3rem 0;">
                <h2>Strathmore University Lost & Found</h2>
                <p style="font-size: 1.1rem; margin: 1rem 0; color: #666;">
                    Help reunite lost items with their owners on campus
                </p>
                <div style="margin-top: 2rem;">
                    <a href="browse.html" class="btn btn-primary" style="margin-right: 1rem;">Browse Items</a>
                    <a href="register.html" class="btn btn-secondary">Get Started</a>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem;">
                <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h3>📱 Easy to Use</h3>
                    <p>Report lost or found items with photos in just a few clicks.</p>
                </div>
                <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h3>🔍 Quick Search</h3>
                    <p>Browse and filter items by category, date, and location.</p>
                </div>
                <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
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
    const logoutLink = document.getElementById('logoutLink');
    
    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'none';
    }
}
