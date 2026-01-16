/**
 * Browse Found Items Module
 */

let currentPage = 1;
const itemsPerPage = 20;

document.addEventListener('DOMContentLoaded', async () => {
    updateNavbar();
    await loadItems(1);
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
}

async function loadItems(page = 1) {
    try {
        currentPage = page;
        const category = document.getElementById('categoryFilter')?.value || '';
        const response = await apiClient.getItems(category, 'found', page);

        displayItems(response.items || []);
        displayPagination(response.pages, response.current_page);
    } catch (error) {
        console.error('Error loading items:', error);
        document.getElementById('itemsList').innerHTML = `<p class="error">Error loading items</p>`;
    }
}

function displayItems(items) {
    const container = document.getElementById('itemsList');

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="no-items"><p>✅ No found items at this time. Check back later!</p></div>';
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="item-card">
            <div class="item-image">
                <img src="/api/items/${item.item_id}/photo" alt="${item.title}" onerror="this.src='/static/images/placeholder.svg'">
                <span class="item-badge">✅ Found</span>
            </div>
            <div class="item-info">
                <h3>${item.title}</h3>
                <p><strong>📁 Category:</strong> ${item.category}</p>
                <p><strong>📍 Location:</strong> ${item.location}</p>
                <p><strong>📅 Date:</strong> ${new Date(item.date).toLocaleDateString()}</p>
                <p>${item.description}</p>
                <div class="item-meta">
                    <span class="status-badge ${item.status}">${item.status}</span>
                </div>
                <div class="item-actions">
                    ${apiClient.getToken() && item.status === 'verified' ? 
                        `<button class="btn btn-secondary" onclick="claimItem(${item.item_id})">🎁 Claim Item</button>` : 
                        `<button class="btn btn-primary" disabled>Login to Claim</button>`
                    }
                </div>
            </div>
        </div>
    `).join('');
}

function displayPagination(totalPages, currentPage) {
    const container = document.getElementById('pagination');
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="pagination">';
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="pagination-btn ${i === currentPage ? 'active' : ''}" onclick="loadItems(${i})">${i}</button>`;
    }
    html += '</div>';
    container.innerHTML = html;
}

function applyFilters() {
    loadItems(1);
}

async function claimItem(itemId) {
    if (!apiClient.getToken()) {
        alert('Please login to claim an item');
        window.location.href = '/login';
        return;
    }

    try {
        await apiClient.claimItem(itemId, 'I believe this is my item');
        alert('✅ Successfully claimed! Admins will verify ownership.');
        loadItems(currentPage);
    } catch (error) {
        alert('❌ ' + error.message);
    }
}
