function getHeaders() {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// ─── Auth ───────────────────────────────────────────────────────────────────

export async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch('/api/auth/login', {
        method: 'POST',
        body: formData
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    return data;
}

export async function register(username, email, password) {
    const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Registration failed');
    }
    return res.json();
}

export async function fetchMe() {
    const res = await fetch('/api/auth/me', { headers: getHeaders() });
    if (res.status === 401) {
        localStorage.removeItem('token');
        return null;
    }
    return res.json();
}

// ─── Individual Portfolio ───────────────────────────────────────────────────

export async function fetchTrades() {
    const res = await fetch('/api/trades', { headers: getHeaders() });
    if (res.status === 401) throw new Error('Unauthorized');
    return res.json();
}

export async function addTrade(trade) {
    const res = await fetch('/api/trades', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(trade)
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to add trade');
    }
    return res.json();
}

export async function deleteTrade(id) {
    const res = await fetch(`/api/trades/${id}`, { 
        method: 'DELETE',
        headers: getHeaders()
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

export async function fetchPortfolioSummary() {
    const res = await fetch('/api/portfolio/summary', { headers: getHeaders() });
    if (res.status === 401) return null;
    return res.json();
}

export async function fetchPortfolioHistory(days = 365) {
    const res = await fetch(`/api/portfolio/chart?days=${days}`, { headers: getHeaders() });
    if (res.status === 401) return [];
    return res.json();
}

export async function deleteCoin(coinId) {
    const res = await fetch(`/api/portfolio/coin/${coinId}`, { 
        method: 'DELETE',
        headers: getHeaders()
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

// ─── Team Endpoints ─────────────────────────────────────────────────────────

export async function fetchTeamSummary() {
    const res = await fetch('/api/team/summary', { headers: getHeaders() });
    if (res.status === 401) return null;
    return res.json();
}

export async function fetchTeamMembers() {
    const res = await fetch('/api/team/members', { headers: getHeaders() });
    if (res.status === 401) return [];
    return res.json();
}

export async function fetchTeamAllocation() {
    const res = await fetch('/api/team/allocation', { headers: getHeaders() });
    if (res.status === 401) return [];
    return res.json();
}

export async function fetchTeamChart(days = 365) {
    const res = await fetch(`/api/team/chart?days=${days}`, { headers: getHeaders() });
    if (res.status === 401) return { team: [], members: {} };
    return res.json();
}

export async function fetchTeamHoldings() {
    const res = await fetch('/api/team/holdings', { headers: getHeaders() });
    if (res.status === 401) return [];
    return res.json();
}

export async function fetchTeamTrades() {
    const res = await fetch('/api/team/trades', { headers: getHeaders() });
    if (res.status === 401) return [];
    return res.json();
}

// ─── Market ─────────────────────────────────────────────────────────────────

export async function searchCoins(query) {
    const res = await fetch(`/api/market/search?query=${encodeURIComponent(query)}`, { headers: getHeaders() });
    return res.json();
}

export async function fetchMarketHistory(coinId, days = 365) {
    const res = await fetch(`/api/market/history/${coinId}?days=${days}`, { headers: getHeaders() });
    return res.json();
}

export async function fetchCoinPrice(coinId) {
    const res = await fetch(`/api/market/price/${coinId}`, { headers: getHeaders() });
    return res.json();
}
