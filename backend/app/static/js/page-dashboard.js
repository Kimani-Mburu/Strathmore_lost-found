/**
 * Dashboard Page Module
 */

document.addEventListener('DOMContentLoaded', async () => {
    updateNavbar();
    await loadAllStats();
});

function updateNavbar() {
    const token = apiClient.getToken();
    document.getElementById('loginLink').style.display = token ? 'none' : 'block';
    document.getElementById('registerLink').style.display = token ? 'none' : 'block';
    document.getElementById('logoutLink').style.display = token ? 'block' : 'none';
    document.getElementById('reportLink').style.display = token ? 'block' : 'none';

    if (token && document.getElementById('logoutLink')) {
        document.getElementById('logoutLink').onclick = (e) => {
            e.preventDefault();
            apiClient.clearToken();
            localStorage.removeItem('user');
            window.location.href = '/';
        };
    }

    // Check if admin
    if (token) {
        apiClient.getProfile()
            .then(profile => {
                if (profile.role === 'admin') {
                    document.getElementById('adminLink').style.display = 'block';
                }
            })
            .catch(() => {});
    }
}

async function loadAllStats() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const items = response.items || [];

        // Overall stats
        const total = items.length;
        const lost = items.filter(i => i.item_type === 'lost').length;
        const found = items.filter(i => i.item_type === 'found').length;
        const reclaimed = items.filter(i => i.status === 'returned').length;
        const recoveryRate = total > 0 ? Math.round((reclaimed / total) * 100) : 0;

        document.getElementById('totalItems').textContent = total;
        document.getElementById('lostItems').textContent = lost;
        document.getElementById('reclaimedItems').textContent = reclaimed;
        document.getElementById('successRate').textContent = recoveryRate + '%';

        // Department stats
        loadDepartmentStats(items);

        // Category stats
        loadCategoryStats(items);

        // Status breakdown
        loadStatusBreakdown(items);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function loadDepartmentStats(items) {
    const depts = {};
    items.forEach(item => {
        const dept = item.location || 'Other';
        depts[dept] = (depts[dept] || 0) + 1;
    });

    const sorted = Object.entries(depts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6);

    document.getElementById('departmentStats').innerHTML = sorted.map(([dept, count]) => `
        <div class="dept-card">
            <h4>📍 ${dept}</h4>
            <div class="dept-count">${count}</div>
            <p>${count === 1 ? 'item' : 'items'}</p>
        </div>
    `).join('') || '<p class="no-items">No location data</p>';
}

function loadCategoryStats(items) {
    const cats = {};
    items.forEach(item => {
        const cat = item.category || 'Other';
        cats[cat] = (cats[cat] || 0) + 1;
    });

    const sorted = Object.entries(cats)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6);

    document.getElementById('categoryStats').innerHTML = sorted.map(([cat, count]) => `
        <div class="dept-card">
            <h4>📁 ${cat}</h4>
            <div class="dept-count">${count}</div>
            <p>${count === 1 ? 'item' : 'items'}</p>
        </div>
    `).join('') || '<p class="no-items">No category data</p>';
}

function loadStatusBreakdown(items) {
    const statuses = {};
    items.forEach(item => {
        const status = item.status || 'unknown';
        statuses[status] = (statuses[status] || 0) + 1;
    });

    const statusLabels = {
        'pending': '⏳ Pending Verification',
        'verified': '✅ Verified',
        'claimed': '🎁 Claimed',
        'returned': '🏁 Returned',
        'rejected': '❌ Rejected'
    };

    document.getElementById('statusBreakdown').innerHTML = Object.entries(statuses).map(([status, count]) => `
        <div class="dept-card">
            <h4>${statusLabels[status] || status}</h4>
            <div class="dept-count">${count}</div>
            <p>${count === 1 ? 'item' : 'items'}</p>
        </div>
    `).join('') || '<p class="no-items">No status data</p>';
}
