/**
 * API Client for Strathmore Lost & Found Application
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    getToken() {
        return this.token;
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const headers = {
            ...options.headers,
        };

        if (this.token && options.method !== 'FormData') {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'An error occurred');
        }
    }

    // Authentication endpoints
    async register(name, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
    }

    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
    }

    async getProfile() {
        return this.request('/auth/profile', {
            method: 'GET'
        });
    }

    // Item endpoints
    async reportItem(formData) {
        const url = `${API_BASE_URL}/items/report`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to report item');
        }
    }

    async getItems(category = '', itemType = '', page = 1) {
        let endpoint = `/items?page=${page}`;
        if (category) endpoint += `&category=${category}`;
        if (itemType) endpoint += `&item_type=${itemType}`;
        
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async getItem(itemId) {
        return this.request(`/items/${itemId}`, {
            method: 'GET'
        });
    }

    async getItemPhoto(itemId) {
        return `${API_BASE_URL}/items/${itemId}/photo`;
    }

    async claimItem(itemId, notes = '') {
        return this.request(`/items/${itemId}/claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes })
        });
    }

    // Admin endpoints
    async getPendingItems() {
        return this.request('/admin/items/pending', {
            method: 'GET'
        });
    }

    async verifyItem(itemId, action) {
        return this.request(`/admin/items/${itemId}/verify`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
    }

    async updateItemStatus(itemId, status) {
        return this.request(`/admin/items/${itemId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
    }
}

// Global API client instance
const apiClient = new APIClient();
