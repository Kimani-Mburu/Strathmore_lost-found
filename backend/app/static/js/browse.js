/**
 * Browse Items Module
 * Handles browsing and filtering items
 */

let currentPage = 1;

async function loadItems() {
    try {
        const itemType = document.getElementById('itemType')?.value || '';
        const category = document.getElementById('category')?.value || '';
        
        const response = await apiClient.getItems(category, itemType, currentPage);
        
        displayItems(response.items);
        displayPagination(response.pages, currentPage);
    } catch (error) {
        console.error('Error loading items:', error);
        document.getElementById('itemsList').innerHTML = `<p>Error loading items: ${error.message}</p>`;
    }
}

function displayItems(items) {
    const itemsList = document.getElementById('itemsList');
    
    if (!items || items.length === 0) {
        itemsList.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No items found.</p>';
        return;
    }
    
    itemsList.innerHTML = items.map(item => `
        <div class="item-card">
            <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
            <div class="item-card-content">
                <div class="item-card-title">${item.title}</div>
                <span class="item-card-category">${item.category}</span>
                <span class="item-card-type">${item.item_type === 'lost' ? '❌ Lost' : '✅ Found'}</span>
                <p class="item-card-description">${item.description}</p>
                <div class="item-card-meta">
                    <p><strong>📍 Location:</strong> ${item.location}</p>
                    <p><strong>📅 Date:</strong> ${new Date(item.date).toLocaleDateString()}</p>
                    <p><strong>Status:</strong> <strong>${item.status}</strong></p>
                </div>
                <div class="item-card-actions">
                    <button class="btn btn-secondary" onclick="viewItem(${item.item_id})">View Details</button>
                    ${apiClient.getToken() && item.status !== 'claimed' ? `<button class="btn btn-success" onclick="claimItemPrompt(${item.item_id})">Claim</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function displayPagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <button 
                class="btn ${i === currentPage ? 'active' : ''}"
                onclick="goToPage(${i})"
            >
                ${i}
            </button>
        `;
    }
    
    pagination.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadItems();
    window.scrollTo(0, 0);
}

function applyFilters() {
    currentPage = 1;
    loadItems();
}

async function claimItemPrompt(itemId) {
    if (!apiClient.getToken()) {
        alert('Please login to claim an item');
        window.location.href = '/login';
        return;
    }
    
    const notes = prompt('Add notes about why you believe this is your item:');
    if (notes !== null) {
        try {
            await apiClient.claimItem(itemId, notes);
            alert('Item claimed successfully! An admin will review your claim.');
            loadItems();
        } catch (error) {
            alert('Error claiming item: ' + error.message);
        }
    }
}

function viewItem(itemId) {
    alert('Item detail view would open here. Item ID: ' + itemId);
}

// Load items on page load
document.addEventListener('DOMContentLoaded', () => {
    updateNavbar();
    loadItems();
});
