/**
 * Report Item Module
 * Handles item reporting with photo upload
 */

if (document.getElementById('reportForm')) {
    document.getElementById('reportForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!apiClient.getToken()) {
            showMessage('Please login to report an item', 'error');
            window.location.href = 'login.html';
            return;
        }
        
        const formData = new FormData();
        formData.append('title', document.getElementById('title').value);
        formData.append('description', document.getElementById('description').value);
        formData.append('category', document.getElementById('category').value);
        formData.append('item_type', document.getElementById('itemType').value);
        formData.append('date', document.getElementById('date').value);
        formData.append('location', document.getElementById('location').value);
        formData.append('photo', document.getElementById('photo').files[0]);
        
        try {
            const response = await apiClient.reportItem(formData);
            showMessage('Item reported successfully! An admin will verify it shortly.', 'success');
            
            // Reset form
            document.getElementById('reportForm').reset();
            
            // Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = 'browse.html';
            }, 2000);
        } catch (error) {
            showMessage(error.message, 'error');
        }
    });
}

function showMessage(message, type = 'info') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = type;
        messageEl.style.display = 'block';
    }
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    if (!apiClient.getToken()) {
        showMessage('Please login to report an item', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    }
});
