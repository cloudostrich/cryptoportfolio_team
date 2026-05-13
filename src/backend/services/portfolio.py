from datetime import datetime, timezone
from ..db import queries
from . import coingecko
from ..models.schemas import Holding, PortfolioSummary


def _compute_holdings_from_trades(trades: list) -> dict:
    """Given a list of trade dicts, compute holdings by coin_id."""
    holdings_dict = {}
    for trade in trades:
        coin_id = trade['coin_id']
        if coin_id not in holdings_dict:
            holdings_dict[coin_id] = {
                'coin_id': coin_id,
                'coin_symbol': trade['coin_symbol'],
                'coin_name': trade['coin_name'],
                'total_amount': 0.0,
                'total_cost_usd': 0.0
            }
        amount = trade['amount']
        cost = trade['price_usd'] * amount
        if trade['trade_type'] == 'buy':
            holdings_dict[coin_id]['total_amount'] += amount
            holdings_dict[coin_id]['total_cost_usd'] += cost
        elif trade['trade_type'] == 'sell':
            holdings_dict[coin_id]['total_amount'] -= amount
            holdings_dict[coin_id]['total_cost_usd'] -= cost
    return {k: v for k, v in holdings_dict.items() if v['total_amount'] > 0.000001}


async def _build_summary(trades: list) -> PortfolioSummary:
    """Build a PortfolioSummary from a list of trades."""
    holdings_dict = _compute_holdings_from_trades(trades)
    coin_ids = list(holdings_dict.keys())
    current_prices = await coingecko.get_current_prices(coin_ids) if coin_ids else {}

    holdings = []
    total_value = 0.0
    total_cost = 0.0
    for coin_id, data in holdings_dict.items():
        price = current_prices.get(coin_id, 0.0)
        value = data['total_amount'] * price
        avg_buy = data['total_cost_usd'] / data['total_amount'] if data['total_amount'] > 0 else 0
        pnl = value - data['total_cost_usd']
        pnl_pct = (pnl / data['total_cost_usd']) * 100 if data['total_cost_usd'] > 0 else 0
        holdings.append(Holding(
            coin_id=coin_id,
            coin_symbol=data['coin_symbol'],
            coin_name=data['coin_name'],
            total_amount=data['total_amount'],
            total_cost_usd=data['total_cost_usd'],
            average_buy_price=avg_buy,
            current_price_usd=price,
            current_value_usd=value,
            pnl_usd=pnl,
            pnl_percentage=pnl_pct
        ))
        total_value += value
        total_cost += data['total_cost_usd']

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    return PortfolioSummary(
        total_value_usd=total_value,
        total_cost_usd=total_cost,
        total_pnl_usd=total_pnl,
        total_pnl_percentage=total_pnl_pct,
        holdings=holdings
    )


async def get_portfolio_summary(user_id: str) -> PortfolioSummary:
    trades = queries.get_all_trades(user_id=user_id)
    return await _build_summary(trades)


async def get_team_summary() -> PortfolioSummary:
    """Aggregate portfolio summary across ALL users."""
    trades = queries.get_all_trades()  # no user_id filter
    return await _build_summary(trades)


async def get_team_members_summary() -> list:
    """Return per-member performance summary for the bar chart."""
    users = queries.get_all_users()
    results = []
    for user in users:
        summary = await get_portfolio_summary(user['id'])
        results.append({
            'user_id': user['id'],
            'username': user['username'],
            'total_value_usd': summary.total_value_usd,
            'total_cost_usd': summary.total_cost_usd,
            'total_pnl_usd': summary.total_pnl_usd,
            'total_pnl_percentage': summary.total_pnl_percentage,
            'num_coins': len(summary.holdings)
        })
    return results


async def get_team_holdings() -> list:
    """Return all members' holdings as a flat list with username attached."""
    users = queries.get_all_users()
    all_holdings = []
    for user in users:
        summary = await get_portfolio_summary(user['id'])
        for h in summary.holdings:
            all_holdings.append({
                'username': user['username'],
                'coin_id': h.coin_id,
                'coin_symbol': h.coin_symbol,
                'coin_name': h.coin_name,
                'total_amount': h.total_amount,
                'total_cost_usd': h.total_cost_usd,
                'average_buy_price': h.average_buy_price,
                'current_price_usd': h.current_price_usd,
                'current_value_usd': h.current_value_usd,
                'pnl_usd': h.pnl_usd,
                'pnl_percentage': h.pnl_percentage
            })
    return all_holdings


async def get_team_allocation() -> list:
    """Return per-member allocation breakdown for the doughnut chart.
    Each entry = { username, coin_name, coin_symbol, value_usd }
    """
    users = queries.get_all_users()
    allocation = []
    for user in users:
        summary = await get_portfolio_summary(user['id'])
        for h in summary.holdings:
            allocation.append({
                'username': user['username'],
                'coin_name': h.coin_name,
                'coin_symbol': h.coin_symbol,
                'value_usd': h.current_value_usd
            })
    return allocation


async def get_portfolio_history(days: int = 365, user_id: str = None) -> list:
    trades = queries.get_all_trades(user_id=user_id)
    if not trades:
        return []

    coin_ids = list(set(t['coin_id'] for t in trades))
    all_history = {}
    for cid in coin_ids:
        all_history[cid] = await coingecko.get_market_chart(cid, days)

    if not all_history:
        return []

    reference_timestamps = []
    for cid in coin_ids:
        if all_history[cid]:
            reference_timestamps = [p[0] for p in all_history[cid]]
            break
    if not reference_timestamps:
        return []

    for cid in coin_ids:
        if all_history[cid]:
            all_history[cid].sort(key=lambda x: x[0])

    history_points = []
    for ts in reference_timestamps:
        total_val = 0.0
        total_cost = 0.0
        for cid in coin_ids:
            price_data = all_history[cid]
            if not price_data:
                continue
            current_price = 0.0
            for p in price_data:
                if p[0] <= ts:
                    current_price = p[1]
                else:
                    break
            balance = 0.0
            cost = 0.0
            for t in trades:
                if t['coin_id'] != cid:
                    continue
                t_ts = t['timestamp']
                if isinstance(t_ts, str):
                    try:
                        t_ts = datetime.fromisoformat(t_ts.replace('Z', '+00:00'))
                    except:
                        pass
                t_val = t_ts.timestamp() * 1000 if hasattr(t_ts, 'timestamp') else 0
                if t_val <= ts:
                    amount = t['amount']
                    trade_cost = t['price_usd'] * amount
                    if t['trade_type'] == 'buy':
                        balance += amount
                        cost += trade_cost
                    else:
                        balance -= amount
                        cost -= trade_cost
            total_val += balance * current_price
            total_cost += cost
        history_points.append([ts, total_val, total_cost])

    # Add a 'now' point
    try:
        if user_id:
            current_summary = await get_portfolio_summary(user_id=user_id)
        else:
            current_summary = await get_team_summary()
        now_ms = datetime.now(timezone.utc).timestamp() * 1000
        history_points.append([now_ms, current_summary.total_value_usd, current_summary.total_cost_usd])
    except:
        pass

    return history_points


async def get_team_history(days: int = 365) -> dict:
    """Return chart history for team overall + per member.
    { "team": [...], "members": { "username": [...], ... } }
    """
    team_history = await get_portfolio_history(days, user_id=None)
    users = queries.get_all_users()
    members = {}
    for user in users:
        member_history = await get_portfolio_history(days, user_id=user['id'])
        if member_history:
            members[user['username']] = member_history
    return {"team": team_history, "members": members}
