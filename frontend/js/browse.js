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
        document.getElementById('itemsList').innerHTML = '<p>Error loading items. Please try again.</p>';
    }
}

function displayItems(items) {
    const itemsList = document.getElementById('itemsList');
    
    if (items.length === 0) {
        itemsList.innerHTML = '<p>No items found.</p>';
        return;
    }
    
    itemsList.innerHTML = items.map(item => `
        <div class="item-card">
            <img src="${item.photo_path}" alt="${item.title}" onerror="this.src='images/placeholder.png'">
            <div class="item-card-content">
                <div class="item-card-title">${item.title}</div>
                <span class="item-card-category">${item.category}</span>
                <span class="item-card-type">${item.item_type === 'lost' ? 'Lost' : 'Found'}</span>
                <p class="item-card-description">${item.description}</p>
                <div class="item-card-meta">
                    <p>Location: ${item.location}</p>
                    <p>Date: ${new Date(item.date).toLocaleDateString()}</p>
                    <p>Status: ${item.status}</p>
                </div>
                <div class="item-card-actions">
                    <button class="btn btn-secondary" onclick="viewItem(${item.item_id})">View</button>
                    ${apiClient.getToken() ? `<button class="btn btn-success" onclick="claimItemPrompt(${item.item_id})">Claim</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function displayPagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
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
        window.location.href = 'login.html';
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
    // Could implement a modal or detail view here
    alert('Item detail view would open here');
}

// Load items on page load
document.addEventListener('DOMContentLoaded', loadItems);
