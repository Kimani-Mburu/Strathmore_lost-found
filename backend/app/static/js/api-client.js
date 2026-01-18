/**
 * API Client for Strathmore Lost & Found Application
 * Handles all communication with the backend API
 */

// Use relative URL for API - will work from same domain
const API_BASE_URL = '/api';

class APIClient {
    constructor() {
        // Don't cache token - always get fresh from localStorage
    }

    getToken() {
        return localStorage.getItem('auth_token');
    }

    setToken(token) {
        localStorage.setItem('auth_token', token);
    }

    clearToken() {
        localStorage.removeItem('auth_token');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        
        const headers = {
            ...options.headers,
        };

        const token = this.getToken();
        if (token && options.method !== 'FormData') {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            if (response.ok) {
                return await response.json();
            } else {
                let error;
                try {
                    error = await response.json();
                } catch (e) {
                    error = { error: `HTTP ${response.status}` };
                }
                throw new Error(error.error || 'An error occurred');
            }
        } catch (error) {
            console.error('API Error:', error);
            throw error;
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
        const token = this.getToken();
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                return await response.json();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to report item');
            }
        } catch (error) {
            console.error('Report item error:', error);
            throw error;
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

    async getMyItems() {
        return this.request('/items/my-items', {
            method: 'GET'
        });
    }

    async getMyClaimStatus(itemId) {
        return this.request(`/items/${itemId}/my-claim`, {
            method: 'GET'
        });
    }

    async getMyAllClaims() {
        return this.request('/items/claims/my-claims', {
            method: 'GET'
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

    // Claims management endpoints
    async getPendingClaims() {
        return this.request('/admin/claims/pending', {
            method: 'GET'
        });
    }

    async getAllClaims(status = '') {
        let endpoint = '/admin/claims/all';
        if (status) endpoint += `?status=${status}`;
        
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    async approveClaim(claimId) {
        return this.request(`/admin/claims/${claimId}/approve`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
    }

    async rejectClaim(claimId) {
        return this.request(`/admin/claims/${claimId}/reject`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
    }

    async updateClaimNotes(claimId, notes) {
        return this.request(`/admin/claims/${claimId}/notes`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes })
        });
    }
}

// Global API client instance
const apiClient = new APIClient();
