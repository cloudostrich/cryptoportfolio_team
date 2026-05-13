/* ─── Chart Module (Lightweight Charts v5 + Chart.js) ────────────────────────
 *  Charts:
 *    1. Holdings chart  – multi-line: team total + per-member lines
 *    2. Performance chart – multi-line: team PnL % + per-member PnL % + BTC %
 *    3. Allocation doughnut – team allocation by member+coin
 *    4. Member bar chart – per-member PnL comparison
 * ──────────────────────────────────────────────────────────────────────────── */

// ─── Theme tokens (shared) ──────────────────────────────────────────────────
const THEME = {
    background: '#181a20',
    text: '#848e9c',
    grid: '#2b3139',
    border: '#2b3139',
    teamLine: '#0ecb81',       // green — team total
    btcLine: '#f0b90b',        // gold
};

// Distinct colors for members
const MEMBER_COLORS = [
    '#5470c6', '#ee6666', '#fac858', '#73c0de', '#fc8452',
    '#9a60b4', '#ea7ccc', '#3ba272', '#91cc75', '#d48265'
];

const CHART_COLORS = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#d48265',
    '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570'
];

// ─── Holdings Chart (multi-line) ────────────────────────────────────────────
let holdingsChart = null;
let holdingsTeamSeries = null;
let holdingsMemberSeries = {}; // keyed by username

function createLWChart(container) {
    return LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight || 300,
        layout: {
            background: { type: 'solid', color: THEME.background },
            textColor: THEME.text,
            attributionLogo: false,
        },
        grid: {
            vertLines: { color: THEME.grid },
            horzLines: { color: THEME.grid },
        },
        rightPriceScale: { borderColor: THEME.border },
        timeScale: { borderColor: THEME.border, timeVisible: true, secondsVisible: false },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    });
}

export function initHoldingsChart(container) {
    if (!container) return;
    if (holdingsChart) holdingsChart.remove();
    holdingsChart = createLWChart(container);
    holdingsTeamSeries = holdingsChart.addSeries(LightweightCharts.LineSeries, {
        color: THEME.teamLine,
        lineWidth: 2,
        title: 'Team',
        priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
    });
    holdingsMemberSeries = {};
    new ResizeObserver(() => {
        if (holdingsChart) holdingsChart.applyOptions({ width: container.clientWidth, height: container.clientHeight || 300 });
    }).observe(container);
}

export function updateHoldingsData(teamData, membersData) {
    if (!holdingsChart) return;

    // Update team line
    if (teamData && teamData.length > 0) {
        holdingsTeamSeries.setData(normalizeTimeSeries(teamData));
    }

    // Remove old member series
    for (const key in holdingsMemberSeries) {
        holdingsChart.removeSeries(holdingsMemberSeries[key]);
    }
    holdingsMemberSeries = {};

    // Add member lines
    const legendEl = document.getElementById('history-legend');
    if (legendEl) legendEl.innerHTML = buildLegendHTML('Team', THEME.teamLine, membersData ? Object.keys(membersData) : []);

    if (membersData) {
        let i = 0;
        for (const [username, data] of Object.entries(membersData)) {
            if (!data || data.length === 0) continue;
            const color = MEMBER_COLORS[i % MEMBER_COLORS.length];
            const series = holdingsChart.addSeries(LightweightCharts.LineSeries, {
                color: color,
                lineWidth: 1,
                title: username,
                priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
            });
            series.setData(normalizeTimeSeries(data));
            holdingsMemberSeries[username] = series;
            i++;
        }
    }
    holdingsChart.timeScale().fitContent();
}

// ─── Performance Chart (multi-line % returns) ───────────────────────────────
let perfChart = null;
let perfTeamSeries = null;
let perfBtcSeries = null;
let perfMemberSeries = {};

export function initPerformanceChart(container) {
    if (!container) return;
    if (perfChart) perfChart.remove();
    perfChart = createLWChart(container);
    perfChart.applyOptions({ timeScale: { timeVisible: false } });

    perfTeamSeries = perfChart.addSeries(LightweightCharts.LineSeries, {
        color: THEME.teamLine,
        lineWidth: 2,
        title: 'Team',
        priceFormat: { type: 'custom', formatter: (v) => v.toFixed(1) + '%' },
    });
    perfBtcSeries = perfChart.addSeries(LightweightCharts.LineSeries, {
        color: THEME.btcLine,
        lineWidth: 2,
        title: 'BTC',
        priceFormat: { type: 'custom', formatter: (v) => v.toFixed(1) + '%' },
    });
    perfMemberSeries = {};
    new ResizeObserver(() => {
        if (perfChart) perfChart.applyOptions({ width: container.clientWidth, height: container.clientHeight || 300 });
    }).observe(container);
}

export function updatePerformanceData(teamData, btcData, membersData) {
    if (!perfChart) return;

    if (teamData && teamData.length > 0) {
        perfTeamSeries.setData(toPortfolioPerformance(teamData));
    }
    if (btcData && btcData.length > 0) {
        perfBtcSeries.setData(toPercentageReturn(btcData));
    }

    // Remove old member series
    for (const key in perfMemberSeries) {
        perfChart.removeSeries(perfMemberSeries[key]);
    }
    perfMemberSeries = {};

    // Build legend
    const legendEl = document.getElementById('perf-legend');
    if (legendEl) legendEl.innerHTML = buildLegendHTML('Team', THEME.teamLine, membersData ? Object.keys(membersData) : [], THEME.btcLine);

    if (membersData) {
        let i = 0;
        for (const [username, data] of Object.entries(membersData)) {
            if (!data || data.length === 0) continue;
            const color = MEMBER_COLORS[i % MEMBER_COLORS.length];
            const series = perfChart.addSeries(LightweightCharts.LineSeries, {
                color: color,
                lineWidth: 1,
                title: username,
                priceFormat: { type: 'custom', formatter: (v) => v.toFixed(1) + '%' },
            });
            series.setData(toPortfolioPerformance(data));
            perfMemberSeries[username] = series;
            i++;
        }
    }
    perfChart.timeScale().fitContent();
}

// ─── Allocation (Donut) Chart – per member ──────────────────────────────────
let allocationChart = null;

export function initAllocationChart(canvasId, legendId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (allocationChart) allocationChart.destroy();

    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [], backgroundColor: [], borderWidth: 0, hoverOffset: 4 }] },
        options: {
            cutout: '65%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: $${ctx.raw.toFixed(2)}`
                    }
                }
            }
        }
    });
}

export function updateAllocationData(allocation, legendId) {
    if (!allocationChart || !allocation) return;

    // allocation is an array of { username, coin_name, coin_symbol, value_usd }
    // Build labels like "BTC (alice)" and assign colors per member
    const memberColorMap = {};
    let colorIdx = 0;
    allocation.forEach(a => {
        if (!memberColorMap[a.username]) {
            memberColorMap[a.username] = MEMBER_COLORS[colorIdx % MEMBER_COLORS.length];
            colorIdx++;
        }
    });

    const valid = allocation.filter(a => a.value_usd > 0).sort((a, b) => b.value_usd - a.value_usd);
    const total = valid.reduce((sum, a) => sum + a.value_usd, 0);

    const labels = valid.map(a => `${a.coin_symbol.toUpperCase()} (${a.username})`);
    const data = valid.map(a => a.value_usd);
    const colors = valid.map(a => {
        // Slightly vary the shade per coin for the same member
        const baseColor = memberColorMap[a.username];
        return baseColor;
    });

    allocationChart.data.labels = labels;
    allocationChart.data.datasets[0].data = data;
    allocationChart.data.datasets[0].backgroundColor = colors;
    allocationChart.update();

    // Custom Legend
    const legend = document.getElementById(legendId);
    if (legend) {
        legend.innerHTML = '';
        valid.forEach((a, i) => {
            const pct = total > 0 ? ((a.value_usd / total) * 100).toFixed(1) : '0.0';
            const row = document.createElement('div');
            row.className = 'legend-row';
            row.innerHTML = `
                <div class="legend-left">
                    <div class="legend-color" style="background-color: ${colors[i]}"></div>
                    <span>${a.coin_symbol.toUpperCase()} <small style="color:var(--text-secondary)">${a.username}</small></span>
                </div>
                <span class="legend-pct">${pct}%</span>
            `;
            legend.appendChild(row);
        });
    }
}

// ─── Member Bar Chart ───────────────────────────────────────────────────────
let memberBarChart = null;

export function initMemberBarChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (memberBarChart) memberBarChart.destroy();

    memberBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'PnL ($)',
                    data: [],
                    backgroundColor: [],
                    borderRadius: 4,
                    barPercentage: 0.6,
                },
                {
                    label: 'PnL (%)',
                    data: [],
                    backgroundColor: [],
                    borderRadius: 4,
                    barPercentage: 0.6,
                    hidden: true,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#848e9c', font: { family: 'Inter' } },
                    onClick: (e, legendItem, legend) => {
                        const ci = legend.chart;
                        // Toggle between PnL $ and PnL %
                        ci.data.datasets.forEach((ds, i) => {
                            ds.hidden = i === legendItem.datasetIndex ? false : true;
                        });
                        ci.update();
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            if (ctx.datasetIndex === 0) return ` PnL: $${ctx.raw.toFixed(2)}`;
                            return ` PnL: ${ctx.raw.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#848e9c' },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: '#848e9c' },
                    grid: { color: '#2b3139' }
                }
            }
        }
    });
}

export function updateMemberBarChart(members) {
    if (!memberBarChart || !members) return;

    const labels = members.map(m => m.username);
    const pnlUsd = members.map(m => m.total_pnl_usd);
    const pnlPct = members.map(m => m.total_pnl_percentage);
    const colors = members.map((m, i) => MEMBER_COLORS[i % MEMBER_COLORS.length]);

    memberBarChart.data.labels = labels;
    memberBarChart.data.datasets[0].data = pnlUsd;
    memberBarChart.data.datasets[0].backgroundColor = colors;
    memberBarChart.data.datasets[1].data = pnlPct;
    memberBarChart.data.datasets[1].backgroundColor = colors;
    memberBarChart.update();
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function normalizeTimeSeries(data) {
    const formatted = data.map(point => ({
        time: Math.floor(point[0] / 1000),
        value: point[1],
    }));
    formatted.sort((a, b) => a.time - b.time);
    const unique = [];
    const seen = new Set();
    for (const pt of formatted) {
        if (!seen.has(pt.time)) {
            seen.add(pt.time);
            unique.push(pt);
        }
    }
    return unique;
}

function toPercentageReturn(data) {
    const points = normalizeTimeSeries(data);
    if (points.length === 0) return [];
    const firstNonZero = points.find(p => p.value !== 0);
    if (!firstNonZero) return points.map(p => ({ time: p.time, value: 0 }));
    const base = firstNonZero.value;
    const baseTime = firstNonZero.time;
    return points.map(p => ({
        time: p.time,
        value: p.time < baseTime ? 0 : ((p.value - base) / base) * 100,
    }));
}

function toPortfolioPerformance(data) {
    if (!data || data.length === 0) return [];
    const points = data.map(p => ({
        time: Math.floor(p[0] / 1000),
        val: p[1],
        cost: p[2]
    })).sort((a, b) => a.time - b.time);

    const unique = [];
    const seen = new Set();
    for (const p of points) {
        if (!seen.has(p.time)) {
            seen.add(p.time);
            const perf = p.cost > 0 ? ((p.val - p.cost) / p.cost) * 100 : 0;
            unique.push({ time: p.time, value: perf });
        }
    }
    return unique;
}

function buildLegendHTML(teamLabel, teamColor, memberNames, btcColor) {
    let html = `<span class="legend-item"><span class="legend-dot" style="background-color:${teamColor}"></span> ${teamLabel}</span>`;
    if (btcColor) {
        html += `<span class="legend-item"><span class="legend-dot" style="background-color:${btcColor}"></span> BTC</span>`;
    }
    memberNames.forEach((name, i) => {
        const color = MEMBER_COLORS[i % MEMBER_COLORS.length];
        html += `<span class="legend-item"><span class="legend-dot" style="background-color:${color}"></span> ${name}</span>`;
    });
    return html;
}
