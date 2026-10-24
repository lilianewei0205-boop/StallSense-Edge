"""Newsvendor inventory decisions: arithmetic is deterministic, never delegated to an LLM."""
from __future__ import annotations
from math import ceil
from statistics import NormalDist


def critical_fractile(unit_cost: float, retail_price: float, salvage_value: float) -> float:
    """Cu/(Cu + Co), where Cu=price-cost and Co=cost-salvage."""
    if unit_cost < 0 or retail_price < 0 or salvage_value < 0:
        raise ValueError("Prices cannot be negative")
    if salvage_value > unit_cost:
        raise ValueError("Salvage value cannot exceed acquisition cost in this prototype")
    shortage_cost = max(0.0, retail_price - unit_cost)
    overage_cost = max(0.0, unit_cost - salvage_value)
    total = shortage_cost + overage_cost
    return shortage_cost / total if total else 0.0


def recommend_order(
    mean_demand: float, sigma: float, current_inventory: float,
    unit_cost: float, retail_price: float, salvage_value: float,
) -> dict:
    if current_inventory < 0 or mean_demand < 0 or sigma < 0:
        raise ValueError("Inventory and demand cannot be negative")
    fractile = critical_fractile(unit_cost, retail_price, salvage_value)
    if fractile <= 0:
        target = 0.0
    elif fractile >= 1:
        # Capped at high percentile to avoid infinitely large orders under normal tails.
        target = mean_demand + NormalDist().inv_cdf(0.999) * sigma
    else:
        alpha = min(0.999, max(0.001, fractile))
        target = mean_demand + NormalDist().inv_cdf(alpha) * sigma
    target = max(0.0, target)
    return {
        "critical_fractile": fractile,
        "target_inventory": target,
        "order_qty": max(0, ceil(target - current_inventory)),
        "shortage_cost_per_unit": max(0., retail_price - unit_cost),
        "leftover_cost_per_unit": max(0., unit_cost - salvage_value),
    }


def simulate_day(demand: float, quantity_ordered: float,
                 unit_cost: float, retail_price: float, salvage_value: float) -> dict:
    """One-day, fully perishable product, no carryover, with OBSERVED true demand.

    True demand is only available in synthetic demonstration data, not usually
    in real retail records; actual stockout demand is censored.
    """
    sales = min(max(0., demand), max(0., quantity_ordered))
    leftovers = max(0., quantity_ordered - demand)
    return {
        "sold": sales,
        "leftover_units": leftovers,
        "leftover_cost": leftovers * (unit_cost - salvage_value),
        "stockout": int(demand > quantity_ordered),
        "estimated_profit": retail_price * sales + salvage_value * leftovers - unit_cost * quantity_ordered,
    }
