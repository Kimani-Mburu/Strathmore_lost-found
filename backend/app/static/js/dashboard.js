/**
 * Dashboard Module
 * Handles statistics and recent items display
 */

document.addEventListener('DOMContentLoaded', async () => {
    updateNavbar();
    await loadDashboardStats();
    await loadDepartmentStats();
    await loadRecentItems();
    setupSearch();
});

function updateNavbar() {
    const token = apiClient.getToken();
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutLink = document.getElementById('logoutLink');
    const reportLink = document.getElementById('reportLink');
    const reportBtn = document.getElementById('reportBtn');

    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
        if (reportLink) reportLink.style.display = 'block';
        if (reportBtn) reportBtn.style.display = 'inline-block';

        // Setup logout
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                apiClient.clearToken();
                localStorage.removeItem('user');
                window.location.href = '/';
            });
        }
    } else {
        if (loginLink) loginLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'none';
        if (reportLink) reportLink.style.display = 'none';
        if (reportBtn) reportBtn.style.display = 'none';
    }
}

async function loadDashboardStats() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const items = response.items || [];

        const total = items.length;
        const lost = items.filter(i => i.item_type === 'lost').length;
        const reclaimed = items.filter(i => i.status === 'returned').length;
        const recoveryRate = total > 0 ? Math.round((reclaimed / total) * 100) : 0;

        document.getElementById('totalItems').textContent = total;
        document.getElementById('lostItems').textContent = lost;
        document.getElementById('reclaimedItems').textContent = reclaimed;
        document.getElementById('successRate').textContent = recoveryRate + '%';
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

async function loadDepartmentStats() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const items = response.items || [];

        // Group by location/department
        const departments = {};
        items.forEach(item => {
            const dept = item.location || 'Other';
            departments[dept] = (departments[dept] || 0) + 1;
        });

        // Sort by count (descending)
        const sorted = Object.entries(departments)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);

        const container = document.getElementById('departmentStats');
        container.innerHTML = sorted.map(([dept, count]) => `
            <div class="dept-card">
                <h4>📍 ${dept}</h4>
                <div class="dept-count">${count}</div>
                <p>${count === 1 ? 'item' : 'items'}</p>
            </div>
        `).join('');

        if (sorted.length === 0) {
            container.innerHTML = '<p class="no-items">No items yet</p>';
        }
    } catch (error) {
        console.error('Error loading department stats:', error);
    }
}

async function loadRecentItems() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const items = (response.items || []).slice(0, 6);

        const container = document.getElementById('recentItems');
        if (items.length === 0) {
            container.innerHTML = '<p class="no-items">No items yet. Be the first to report one!</p>';
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="item-card">
                <div class="item-image">
                    <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
                    <span class="item-badge">${item.item_type === 'lost' ? '❌ Lost' : '✅ Found'}</span>
                </div>
                <div class="item-info">
                    <h3>${item.title}</h3>
                    <p><strong>Category:</strong> ${item.category}</p>
                    <p><strong>Location:</strong> ${item.location}</p>
                    <p><strong>Date:</strong> ${new Date(item.date).toLocaleDateString()}</p>
                    <div class="item-meta">
                        <span class="status-badge ${item.status}">${item.status}</span>
                    </div>
                    <div class="item-actions">
                        <a href="/browse-${item.item_type === 'lost' ? 'lost' : 'found'}" class="btn btn-secondary btn-small">View More</a>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent items:', error);
        document.getElementById('recentItems').innerHTML = '<p class="error">Error loading items</p>';
    }
}

function setupSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
}

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    // For now, redirect to browse page with search term in session
    sessionStorage.setItem('searchQuery', query);
    window.location.href = '/browse-lost';
}
