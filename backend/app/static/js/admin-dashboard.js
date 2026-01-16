/**
 * Admin Dashboard Module
 * Handles item verification and management
 */

let currentTab = 'pending';

// Check admin access on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('admin-dashboard.js: DOMContentLoaded');
    updateNavbar();
    
    const token = apiClient.getToken();
    console.log('admin-dashboard.js: Token found:', token ? 'YES' : 'NO');
    
    if (!token) {
        console.log('admin-dashboard.js: No token, redirecting to login');
        showMessage('Admin access required. Please login.', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return;
    }
    
    // Check if user is admin
    try {
        console.log('admin-dashboard.js: Fetching profile...');
        const profile = await apiClient.getProfile();
        console.log('admin-dashboard.js: Profile loaded:', profile);
        
        if (profile.role !== 'admin') {
            console.error('admin-dashboard.js: User is not admin, role:', profile.role);
            showMessage('❌ Admin access required. You do not have permission to access this page.', 'error');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        console.log('admin-dashboard.js: User is admin, loading content');
        // User is admin, load content
        loadPendingItems();
    } catch (error) {
        console.error('admin-dashboard.js: Error checking admin access:', error);
        showMessage('Error verifying admin access: ' + error.message, 'error');
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

function switchTab(tabName) {
    currentTab = tabName;
    
    // Update button states
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.admin-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Load content
    if (tabName === 'pending') loadPendingItems();
    else if (tabName === 'verified') loadVerifiedItems();
    else if (tabName === 'claims') loadPendingClaims();
    else if (tabName === 'claimed') loadClaimedItems();
    else if (tabName === 'rejected') loadRejectedItems();
}

async function loadPendingItems() {
    try {
        const response = await apiClient.getPendingItems();
        displayPendingItems(response.items || []);
        document.getElementById('pendingCount').textContent = response.items?.length || 0;
    } catch (error) {
        console.error('Error loading pending items:', error);
        document.getElementById('pendingItemsList').innerHTML = `<p class="error">Error loading items: ${error.message}</p>`;
    }
}

async function loadPendingClaims() {
    try {
        const response = await apiClient.getPendingClaims();
        displayPendingClaims(response.claims || []);
        document.getElementById('claimsCount').textContent = response.claims?.length || 0;
    } catch (error) {
        console.error('Error loading pending claims:', error);
        document.getElementById('pendingClaimsList').innerHTML = `<p class="error">Error loading claims: ${error.message}</p>`;
    }
}

async function loadVerifiedItems() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const verified = response.items?.filter(item => item.status === 'verified') || [];
        displayVerifiedItems(verified);
    } catch (error) {
        console.error('Error loading verified items:', error);
        document.getElementById('verifiedItemsList').innerHTML = `<p class="error">Error loading items</p>`;
    }
}

async function loadClaimedItems() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const claimed = response.items?.filter(item => item.status === 'claimed') || [];
        displayClaimedItems(claimed);
    } catch (error) {
        console.error('Error loading claimed items:', error);
        document.getElementById('claimedItemsList').innerHTML = `<p class="error">Error loading items</p>`;
    }
}

async function loadRejectedItems() {
    try {
        const response = await apiClient.getItems('', '', 1);
        const rejected = response.items?.filter(item => item.status === 'rejected') || [];
        displayRejectedItems(rejected);
    } catch (error) {
        console.error('Error loading rejected items:', error);
        document.getElementById('rejectedItemsList').innerHTML = `<p class="error">Error loading items</p>`;
    }
}

function displayPendingItems(items) {
    const container = document.getElementById('pendingItemsList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>✅ No pending items. All items verified!</p></div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="admin-item-card">
            <div class="admin-item-image">
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
                <span class="admin-item-badge">${item.item_type === 'lost' ? '❌ Lost' : '✅ Found'}</span>
            </div>
            <div class="admin-item-info">
                <h3>${item.title}</h3>
                <p><strong>Category:</strong> ${item.category}</p>
                <p><strong>Description:</strong> ${item.description.substring(0, 100)}...</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <p><strong>Date:</strong> ${new Date(item.date).toLocaleDateString()}</p>
                <p><strong>Reported by:</strong> User #${item.user_id}</p>
                <div class="admin-item-actions">
                    <button class="btn btn-success" onclick="verifyItem(${item.item_id})">✅ Approve</button>
                    <button class="btn btn-danger" onclick="rejectItem(${item.item_id})">❌ Reject</button>
                    <button class="btn btn-secondary" onclick="viewFullDetails(${item.item_id})">👁️ View</button>
                </div>
            </div>
        </div>
    `).join('');
}

function displayPendingClaims(claims) {
    const container = document.getElementById('pendingClaimsList');
    
    if (!claims || claims.length === 0) {
        container.innerHTML = '<div class="no-items"><p>✅ No pending claims!</p></div>';
        return;
    }
    
    container.innerHTML = claims.map(claim => `
        <div class="admin-claim-card">
            <div class="admin-claim-header">
                <h3>Claim #${claim.claim_id}</h3>
                <span class="admin-claim-badge pending">⏳ PENDING</span>
            </div>
            <div class="admin-claim-body">
                <div class="claim-section">
                    <strong>📦 Item Details:</strong>
                    <p>Title: ${claim.item?.title || 'N/A'}</p>
                    <p>Category: ${claim.item?.category || 'N/A'}</p>
                    <p>Original Reporter: ${claim.item_reporter?.email || 'Unknown'}</p>
                </div>
                <div class="claim-section">
                    <strong>👤 Claimant Details:</strong>
                    <p>Email: ${claim.claimer?.email || 'Unknown'}</p>
                    <p>Name: ${claim.claimer?.name || 'Unknown'}</p>
                </div>
                <div class="claim-section">
                    <strong>📝 Claim Notes/Evidence:</strong>
                    <p>${claim.notes || '(No notes provided)'}</p>
                </div>
                <div class="claim-section">
                    <strong>📅 Claim Date:</strong>
                    <p>${new Date(claim.claim_date).toLocaleString()}</p>
                </div>
                <div class="admin-claim-actions">
                    <button class="btn btn-success" onclick="approveClaim(${claim.claim_id})">✅ Approve Claim</button>
                    <button class="btn btn-danger" onclick="rejectClaim(${claim.claim_id})">❌ Reject Claim</button>
                    <button class="btn btn-secondary" onclick="viewClaimDetails(${claim.claim_id})">👁️ View Item Photo</button>
                </div>
            </div>
        </div>
    `).join('');
}

function displayVerifiedItems(items) {
    const container = document.getElementById('verifiedItemsList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>No verified items yet</p></div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="admin-item-card">
            <div class="admin-item-image">
                <img src="${item.photo_path || '/static/images/placeholder.svg'}" alt="${item.title}">
                <span class="admin-item-badge verified">✅ VERIFIED</span>
            </div>
            <div class="admin-item-info">
                <h3>${item.title}</h3>
                <p><strong>Category:</strong> ${item.category}</p>
                <p><strong>Status:</strong> ${item.status}</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <div class="admin-item-actions">
                    <button class="btn btn-warning" onclick="changeStatus(${item.item_id}, 'pending')">↩️ Revert</button>
                </div>
            </div>
        </div>
    `).join('');
}

function displayClaimedItems(items) {
    const container = document.getElementById('claimedItemsList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>No claimed items</p></div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="admin-item-card">
            <div class="admin-item-image">
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
                <span class="admin-item-badge claimed">🎁 CLAIMED</span>
            </div>
            <div class="admin-item-info">
                <h3>${item.title}</h3>
                <p><strong>Category:</strong> ${item.category}</p>
                <p><strong>Status:</strong> ${item.status}</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <p class="note">⚠️ Claimed by user. Contact user to verify ownership before handing over.</p>
                <div class="admin-item-actions">
                    <button class="btn btn-success" onclick="markAsReturned(${item.item_id})">🏁 Mark Returned</button>
                    <button class="btn btn-secondary" onclick="viewFullDetails(${item.item_id})">👁️ View</button>
                </div>
            </div>
        </div>
    `).join('');
}

function displayRejectedItems(items) {
    const container = document.getElementById('rejectedItemsList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>No rejected items</p></div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="admin-item-card rejected">
            <div class="admin-item-image">
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'" style="opacity: 0.5;">
                <span class="admin-item-badge rejected">❌ REJECTED</span>
            </div>
            <div class="admin-item-info">
                <h3>${item.title}</h3>
                <p><strong>Reason:</strong> Insufficient details or suspicious activity</p>
                <div class="admin-item-actions">
                    <button class="btn btn-secondary" onclick="changeStatus(${item.item_id}, 'pending')">🔄 Re-review</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function verifyItem(itemId) {
    if (confirm('Approve this item for listing?')) {
        try {
            await apiClient.verifyItem(itemId, 'approve');
            alert('✅ Item approved and is now visible to users!');
            loadPendingItems();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function rejectItem(itemId) {
    const reason = prompt('Enter rejection reason (brief):');
    if (reason) {
        try {
            await apiClient.verifyItem(itemId, 'reject');
            alert('❌ Item rejected. User will be notified.');
            loadPendingItems();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function changeStatus(itemId, newStatus) {
    try {
        await apiClient.updateItemStatus(itemId, newStatus);
        alert('✅ Status updated');
        loadPendingItems();
        loadVerifiedItems();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function markAsReturned(itemId) {
    if (confirm('Mark this item as returned to the owner?')) {
        try {
            await apiClient.updateItemStatus(itemId, 'returned');
            alert('✅ Item marked as returned!');
            loadClaimedItems();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function viewFullDetails(itemId) {
    try {
        const item = await apiClient.getItem(itemId);
        const modal = document.getElementById('itemModal');
        const details = document.getElementById('modalItemDetails');
        
        details.innerHTML = `
            <div class="modal-item-detail">
                <h3>${item.title}</h3>
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'" style="max-width: 400px; width: 100%; margin: 20px 0; border-radius: 8px;">
                <div class="detail-row">
                    <strong>Type:</strong> ${item.item_type === 'lost' ? '❌ Lost Item' : '✅ Found Item'}
                </div>
                <div class="detail-row">
                    <strong>Category:</strong> ${item.category}
                </div>
                <div class="detail-row">
                    <strong>Description:</strong> ${item.description}
                </div>
                <div class="detail-row">
                    <strong>Location:</strong> ${item.location}
                </div>
                <div class="detail-row">
                    <strong>Date:</strong> ${new Date(item.date).toLocaleString()}
                </div>
                <div class="detail-row">
                    <strong>Status:</strong> <span class="status-badge">${item.status}</span>
                </div>
                <div class="detail-row">
                    <strong>Verified:</strong> ${item.is_verified ? '✅ Yes' : '❌ No'}
                </div>
                <div class="detail-row">
                    <strong>Reported:</strong> ${new Date(item.created_at).toLocaleString()}
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        alert('Error loading details: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('itemModal').style.display = 'none';
}

async function approveClaim(claimId) {
    if (confirm('Approve this claim? The item will be marked as claimed.')) {
        try {
            await apiClient.approveClaim(claimId);
            alert('✅ Claim approved! Item status updated to claimed.');
            loadPendingClaims();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function rejectClaim(claimId) {
    const reason = prompt('Enter reason for rejecting the claim:');
    if (reason !== null) {
        try {
            await apiClient.rejectClaim(claimId);
            alert('❌ Claim rejected. Claimant will be notified.');
            loadPendingClaims();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function viewClaimDetails(claimId) {
    try {
        const response = await apiClient.getPendingClaims();
        const claim = response.claims.find(c => c.claim_id === claimId);
        
        if (!claim) {
            alert('Claim not found');
            return;
        }
        
        const modal = document.getElementById('itemModal');
        const details = document.getElementById('modalItemDetails');
        
        details.innerHTML = `
            <div class="modal-claim-detail">
                <h3>Claim #${claim.claim_id} - Item Details</h3>
                <img src="/api/items/${claim.item?.item_id}/photo" alt="${claim.item?.title}" onerror="this.src='/static/images/placeholder.svg'" style="max-width: 400px; width: 100%; margin: 20px 0; border-radius: 8px;">
                <div class="detail-row">
                    <strong>Item Title:</strong> ${claim.item?.title}
                </div>
                <div class="detail-row">
                    <strong>Category:</strong> ${claim.item?.category}
                </div>
                <div class="detail-row">
                    <strong>Type:</strong> ${claim.item?.item_type === 'lost' ? '❌ Lost' : '✅ Found'}
                </div>
                <div class="detail-row">
                    <strong>Description:</strong> ${claim.item?.description}
                </div>
                <div class="detail-row">
                    <strong>Location:</strong> ${claim.item?.location}
                </div>
                <div class="detail-row">
                    <strong>Item Reporter Email:</strong> ${claim.item_reporter?.email}
                </div>
                <div class="detail-row">
                    <strong>Claimant Email:</strong> ${claim.claimer?.email}
                </div>
                <div class="detail-row">
                    <strong>Claim Evidence:</strong> ${claim.notes || '(No evidence provided)'}
                </div>
                <div class="detail-row">
                    <strong>Compare:</strong> Do the item details match the claimant's story?
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        alert('Error loading claim details: ' + error.message);
    }
}

function updateNavbar() {
    const token = apiClient.getToken();
    const logoutLink = document.getElementById('logoutLink');
    
    if (token) {
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        if (logoutLink) logoutLink.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('itemModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
