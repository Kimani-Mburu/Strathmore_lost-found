/**
 * User Dashboard Module
 * Handles user's reported items and claims
 */

let currentDashboardTab = 'my-items';

// Check authentication on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('my-dashboard.js: DOMContentLoaded');
    updateNavbar();
    
    const token = apiClient.getToken();
    console.log('my-dashboard.js: Token found:', token ? 'YES' : 'NO');
    
    if (!token) {
        console.log('my-dashboard.js: No token, redirecting to login');
        showMessage('Please login to view your dashboard', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return;
    }
    
    try {
        console.log('my-dashboard.js: Fetching profile...');
        const profile = await apiClient.getProfile();
        console.log('my-dashboard.js: Profile loaded:', profile);
        document.getElementById('welcomeMessage').textContent = `Welcome back, ${profile.name}!`;
        
        loadMyItems();
    } catch (error) {
        console.error('my-dashboard.js: Error loading profile:', error);
        showMessage('Error loading profile: ' + error.message, 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
});

// Handle logout
document.getElementById('logoutLink').addEventListener('click', (e) => {
    e.preventDefault();
    apiClient.clearToken();
    localStorage.removeItem('user');
    updateNavbar();
    window.location.href = '/';
});

function switchDashboardTab(tabName) {
    currentDashboardTab = tabName;
    
    // Update button states
    document.querySelectorAll('.dashboard-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.dashboard-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Load content
    if (tabName === 'my-items') loadMyItems();
    else if (tabName === 'my-claims') loadMyClaims();
}

async function loadMyItems() {
    try {
        const response = await apiClient.getMyItems();
        displayMyItems(response.items || []);
        document.getElementById('itemsCount').textContent = response.items?.length || 0;
    } catch (error) {
        console.error('Error loading my items:', error);
        document.getElementById('myItemsList').innerHTML = `<p class="error">Error loading items: ${error.message}</p>`;
    }
}

async function loadMyClaims() {
    try {
        const response = await apiClient.getMyAllClaims();
        displayMyClaims(response.claims || []);
        document.getElementById('claimsCount').textContent = response.claims?.length || 0;
    } catch (error) {
        console.error('Error loading my claims:', error);
        document.getElementById('myClaimsList').innerHTML = `<p class="error">Error loading claims: ${error.message}</p>`;
    }
}

function displayMyItems(items) {
    const container = document.getElementById('myItemsList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>📭 You haven\'t reported any items yet. <a href="/report">Report an item →</a></p></div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="user-item-card">
            <div class="user-item-image">
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
                <span class="item-type-badge ${item.item_type}">${item.item_type === 'lost' ? '❌ Lost' : '✅ Found'}</span>
            </div>
            <div class="user-item-info">
                <h3>${item.title}</h3>
                <p><strong>Category:</strong> ${item.category}</p>
                <p><strong>Description:</strong> ${item.description.substring(0, 80)}...</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <p><strong>Date:</strong> ${new Date(item.date).toLocaleDateString()}</p>
                <div class="status-info">
                    <p><strong>Status:</strong> <span class="status-badge ${item.status}">${item.status.toUpperCase()}</span></p>
                    <p><strong>Verified:</strong> ${item.is_verified ? '✅ Yes' : '⏳ Pending Admin Review'}</p>
                </div>
                <div class="user-item-actions">
                    <button class="btn btn-secondary" onclick="viewItemDetails(${item.item_id})">👁️ View Details</button>
                </div>
            </div>
        </div>
    `).join('');
}

function displayMyClaims(claims) {
    const container = document.getElementById('myClaimsList');
    
    if (!claims || claims.length === 0) {
        container.innerHTML = '<div class="no-items"><p>📭 You haven\'t made any claims yet. <a href="/browse">Browse items →</a></p></div>';
        return;
    }
    
    container.innerHTML = claims.map(claim => `
        <div class="user-claim-card">
            <div class="claim-header">
                <h3>Claim #${claim.claim_id}</h3>
                <span class="claim-status-badge ${claim.status}">${claim.status.toUpperCase()}</span>
            </div>
            <div class="claim-body">
                <p><strong>Item:</strong> ${claim.item?.title || 'Unknown Item'}</p>
                <p><strong>Category:</strong> ${claim.item?.category || 'N/A'}</p>
                <p><strong>Your Evidence:</strong> ${claim.notes || '(No details provided)'}</p>
                <p><strong>Claim Date:</strong> ${new Date(claim.claim_date).toLocaleString()}</p>
                <p><strong>Status:</strong></p>
                <ul>
                    <li>
                        ${claim.status === 'pending' ? '⏳ Waiting for admin review' : ''}
                        ${claim.status === 'approved' ? '✅ Approved - Item is yours!' : ''}
                        ${claim.status === 'rejected' ? '❌ Rejected - Admin review denied' : ''}
                    </li>
                </ul>
            </div>
        </div>
    `).join('');
}

async function viewItemDetails(itemId) {
    try {
        const item = await apiClient.getItem(itemId);
        
        const detailsText = `
Item: ${item.title}
Type: ${item.item_type === 'lost' ? 'Lost' : 'Found'}
Category: ${item.category}
Description: ${item.description}
Location: ${item.location}
Date: ${new Date(item.date).toLocaleString()}
Status: ${item.status}
Verified: ${item.is_verified ? 'Yes' : 'No'}
        `;
        
        alert(detailsText);
    } catch (error) {
        alert('Error loading item details: ' + error.message);
    }
}

function updateNavbar() {
    const token = apiClient.getToken();
    const logoutLink = document.getElementById('logoutLink');
    const reportLink = document.getElementById('reportLink');
    
    if (token) {
        if (logoutLink) logoutLink.style.display = 'block';
        if (reportLink) reportLink.style.display = 'block';
    } else {
        if (logoutLink) logoutLink.style.display = 'none';
        if (reportLink) reportLink.style.display = 'none';
    }
}
