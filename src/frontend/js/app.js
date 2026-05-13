import { 
    fetchTrades, addTrade, deleteTrade,
    fetchPortfolioSummary, fetchTeamSummary, fetchTeamMembers,
    fetchTeamAllocation, fetchTeamChart, fetchTeamHoldings, fetchTeamTrades,
    searchCoins, fetchMarketHistory, fetchCoinPrice, deleteCoin,
    login, register, fetchMe
} from './api.js';

import { 
    initHoldingsChart, updateHoldingsData, 
    initPerformanceChart, updatePerformanceData,
    initAllocationChart, updateAllocationData,
    initMemberBarChart, updateMemberBarChart
} from './chart.js';

// DOM Elements
const totalValueEl = document.getElementById('total-value');
const totalPnlEl = document.getElementById('total-pnl');
const memberValueEl = document.getElementById('member-value');
const memberPnlEl = document.getElementById('member-pnl');
const memberNameLabel = document.getElementById('member-name-label');
const memberPnlLabel = document.getElementById('member-pnl-label');
const logoMemberEl = document.getElementById('logo-member');
const holdingsBody = document.getElementById('holdings-body');
const tradesBody = document.getElementById('trades-body');
const tradeForm = document.getElementById('trade-form');
const coinSearch = document.getElementById('coin-search');
const searchResults = document.getElementById('search-results');
const historyView = document.getElementById('history-view');
const allocationView = document.getElementById('allocation-view');
const coinCountBadge = document.getElementById('coin-count-badge');

// Auth Elements
const authOverlay = document.getElementById('auth-overlay');
const appMain = document.getElementById('app-main');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const showSignup = document.getElementById('show-signup');
const showLogin = document.getElementById('show-login');
const logoutBtn = document.getElementById('logout-btn');
const currentUsernameEl = document.getElementById('current-username');

// State
let debounceTimer;
let currentChartDays = 1;
let currentUser = null;

// Utilities
function formatUsd(val) {
    if (typeof val !== 'number') val = 0;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
}

function formatPct(val) {
    if (typeof val !== 'number') val = 0;
    return new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 2 }).format(val / 100);
}

// ─── Auth Logic ─────────────────────────────────────────────────────────────

async function checkAuth() {
    const user = await fetchMe();
    if (user) {
        currentUser = user;
        showApp();
    } else {
        showAuthUI();
    }
}

function showApp() {
    authOverlay.classList.add('hidden');
    appMain.classList.remove('hidden');
    currentUsernameEl.textContent = currentUser.username;
    logoMemberEl.textContent = `: ${currentUser.username}`;
    memberNameLabel.textContent = `${currentUser.username} Value:`;
    memberPnlLabel.textContent = `${currentUser.username} PnL:`;
    loadDashboard();
}

function showAuthUI() {
    authOverlay.classList.remove('hidden');
    appMain.classList.add('hidden');
}

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await login(
            document.getElementById('login-username').value,
            document.getElementById('login-password').value
        );
        await checkAuth();
    } catch (err) {
        alert(err.message);
    }
});

signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await register(
            document.getElementById('signup-username').value,
            document.getElementById('signup-email').value,
            document.getElementById('signup-password').value
        );
        alert('Account created! Please login.');
        signupForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        document.getElementById('auth-subtitle').textContent = 'Login to manage your portfolio';
    } catch (err) {
        alert(err.message);
    }
});

showSignup.onclick = (e) => {
    e.preventDefault();
    loginForm.classList.add('hidden');
    signupForm.classList.remove('hidden');
    document.getElementById('auth-subtitle').textContent = 'Create your account';
};

showLogin.onclick = (e) => {
    e.preventDefault();
    signupForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
    document.getElementById('auth-subtitle').textContent = 'Login to manage your portfolio';
};

logoutBtn.onclick = () => {
    localStorage.removeItem('token');
    currentUser = null;
    showAuthUI();
};

// ─── Dashboard Logic ────────────────────────────────────────────────────────

async function loadDashboard() {
    try {
        document.body.classList.add('loading-data');
        const [teamSummary, mySummary, teamHoldings, teamTrades, members, allocation] = await Promise.all([
            fetchTeamSummary(),
            fetchPortfolioSummary(),
            fetchTeamHoldings(),
            fetchTeamTrades(),
            fetchTeamMembers(),
            fetchTeamAllocation()
        ]);

        // Header stats: team totals + individual member stats
        renderTeamStats(teamSummary);
        renderMemberStats(mySummary);
        // Holdings table shows ALL team holdings with trader name
        renderHoldings(teamHoldings);
        // Trade history shows ALL team trades with trader name
        renderTrades(teamTrades);
        updateCoinCount(mySummary);

        // Charts
        await Promise.all([
            loadTeamCharts(currentChartDays),
            updateAllocationData(allocation, 'allocation-legend'),
            updateMemberBarChart(members)
        ]);
    } catch (e) {
        console.error("Error loading dashboard:", e);
    } finally {
        document.body.classList.remove('loading-data');
    }
}

async function loadTeamCharts(days) {
    currentChartDays = days;
    try {
        const [chartData, btcData] = await Promise.all([
            fetchTeamChart(days),
            fetchMarketHistory('bitcoin', days <= 30 ? days : 180)
        ]);
        
        // History chart: team + member lines
        updateHoldingsData(chartData.team, chartData.members);
        
        // Performance chart: team + member + BTC lines
        if (days <= 30) {
            const longChart = await fetchTeamChart(180);
            updatePerformanceData(longChart.team, btcData, longChart.members);
        } else {
            updatePerformanceData(chartData.team, btcData, chartData.members);
        }
    } catch (e) {
        console.error("Error loading team charts:", e);
    }
}

function updateCoinCount(summary) {
    if (!coinCountBadge || !summary) return;
    const count = summary.holdings ? summary.holdings.length : 0;
    coinCountBadge.textContent = `${count}/5 coins`;
    coinCountBadge.style.color = count >= 5 ? 'var(--danger)' : 'var(--text-secondary)';
}

// ─── Rendering ──────────────────────────────────────────────────────────────

function renderTeamStats(summary) {
    if (!summary) return;
    totalValueEl.textContent = formatUsd(summary.total_value_usd);
    totalPnlEl.textContent = `${formatUsd(summary.total_pnl_usd)} (${formatPct(summary.total_pnl_percentage)})`;
    totalPnlEl.className = summary.total_pnl_usd >= 0 ? 'stat-value positive' : 'stat-value negative';
}

function renderMemberStats(summary) {
    if (!summary) return;
    memberValueEl.textContent = formatUsd(summary.total_value_usd);
    memberPnlEl.textContent = `${formatUsd(summary.total_pnl_usd)} (${formatPct(summary.total_pnl_percentage)})`;
    memberPnlEl.className = summary.total_pnl_usd >= 0 ? 'stat-value positive' : 'stat-value negative';
}

function renderHoldings(holdings) {
    if (!holdingsBody) return;
    holdingsBody.innerHTML = '';
    if (!holdings || holdings.length === 0) return;
    
    holdings.forEach(h => {
        const tr = document.createElement('tr');
        const pnlClass = h.pnl_usd >= 0 ? 'positive' : 'negative';
        const isOwn = currentUser && h.username === currentUser.username;
        tr.innerHTML = `
            <td><strong>${h.username}</strong></td>
            <td><strong>${h.coin_name}</strong> <span class="coin-symbol">${h.coin_symbol.toUpperCase()}</span></td>
            <td>${h.total_amount.toFixed(4)}</td>
            <td>${formatUsd(h.average_buy_price)}</td>
            <td>${formatUsd(h.current_price_usd)}</td>
            <td>${formatUsd(h.current_value_usd)}</td>
            <td class="${pnlClass}">${formatUsd(h.pnl_usd)} (${formatPct(h.pnl_percentage)})</td>
            <td>${isOwn ? `<button class="btn btn-danger btn-sm btn-delete-holding" data-id="${h.coin_id}">Delete</button>` : ''}</td>
        `;
        holdingsBody.appendChild(tr);
    });

    document.querySelectorAll('.btn-delete-holding').forEach(btn => {
        btn.onclick = async () => {
            const coinId = btn.getAttribute('data-id');
            if (confirm(`Delete all your trades for this coin?`)) {
                await deleteCoin(coinId);
                loadDashboard();
            }
        };
    });
}

function renderTrades(trades) {
    if (!tradesBody || !trades) return;
    tradesBody.innerHTML = '';
    trades.forEach(t => {
        const tr = document.createElement('tr');
        const date = new Date(t.timestamp).toLocaleString();
        const typeColor = t.trade_type === 'buy' ? 'var(--success)' : 'var(--danger)';
        const isOwn = currentUser && t.username === currentUser.username;
        tr.innerHTML = `
            <td><strong>${t.username || '—'}</strong></td>
            <td>${date}</td>
            <td style="color:${typeColor};font-weight:bold;text-transform:uppercase;">${t.trade_type}</td>
            <td>${t.coin_name} (${t.coin_symbol.toUpperCase()})</td>
            <td>${t.amount}</td>
            <td>${formatUsd(t.price_usd)}</td>
            <td>${isOwn ? `<button class="btn btn-danger btn-sm btn-delete-trade" data-id="${t.id}">Delete</button>` : ''}</td>
        `;
        tradesBody.appendChild(tr);
    });

    document.querySelectorAll('.btn-delete-trade').forEach(btn => {
        btn.onclick = async () => {
            if (confirm("Delete this trade?")) {
                await deleteTrade(btn.getAttribute('data-id'));
                loadDashboard();
            }
        };
    });
}

// ─── Coin Search ────────────────────────────────────────────────────────────

coinSearch.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const q = coinSearch.value.trim();
    if (q.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }
    debounceTimer = setTimeout(async () => {
        try {
            const results = await searchCoins(q);
            searchResults.innerHTML = '';
            if (results?.length > 0) {
                results.slice(0, 10).forEach(c => {
                    const li = document.createElement('li');
                    li.innerHTML = `<span>${c.name}</span> <span class="coin-symbol">${c.symbol.toUpperCase()}</span>`;
                    li.onclick = async () => {
                        document.getElementById('selected-coin-id').value = c.id;
                        document.getElementById('selected-coin-symbol').value = c.symbol;
                        document.getElementById('selected-coin-name').value = c.name;
                        coinSearch.value = `${c.name} (${c.symbol.toUpperCase()})`;
                        searchResults.classList.add('hidden');
                        try {
                            const { price } = await fetchCoinPrice(c.id);
                            if (price) document.getElementById('price').value = price;
                        } catch (err) { /* ignore */ }
                    };
                    searchResults.appendChild(li);
                });
                searchResults.classList.remove('hidden');
            }
        } catch (err) { console.error(err); }
    }, 300);
});

document.addEventListener('click', (e) => {
    if (!e.target.closest('.form-group')) searchResults.classList.add('hidden');
});

// ─── Trade Form ─────────────────────────────────────────────────────────────

tradeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const trade = {
        coin_id: document.getElementById('selected-coin-id').value,
        coin_symbol: document.getElementById('selected-coin-symbol').value,
        coin_name: document.getElementById('selected-coin-name').value,
        amount: parseFloat(document.getElementById('amount').value),
        price_usd: parseFloat(document.getElementById('price').value),
        trade_type: document.getElementById('type').value
    };
    if (!trade.coin_id) {
        alert("Please select a coin from the search dropdown.");
        return;
    }
    try {
        await addTrade(trade);
        tradeForm.reset();
        document.getElementById('selected-coin-id').value = '';
        loadDashboard();
    } catch (err) {
        alert(err.message);
    }
});

// ─── Chart Toggles ──────────────────────────────────────────────────────────

document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.getAttribute('data-view');
        if (view === 'history') {
            historyView.classList.remove('hidden');
            allocationView.classList.add('hidden');
        } else {
            historyView.classList.add('hidden');
            allocationView.classList.remove('hidden');
        }
    };
});

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadTeamCharts(parseInt(btn.getAttribute('data-days')));
    };
});

document.getElementById('refresh-btn').onclick = () => loadDashboard();

// ─── Initialization ─────────────────────────────────────────────────────────

function init() {
    initHoldingsChart(document.getElementById('holdings-chart-container'));
    initPerformanceChart(document.getElementById('perf-chart-container'));
    initAllocationChart('allocation-chart', 'allocation-legend');
    initMemberBarChart('member-bar-chart');
    checkAuth();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
