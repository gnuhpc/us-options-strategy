#!/usr/bin/env python3
"""
US Stock Options Fetcher
Fetches options chain data from Yahoo Finance via yfinance.
Outputs structured JSON for the strategy analyzer.
"""

import json
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime, date


def fetch_options(ticker_symbol: str, num_expirations: int = 3):
    """
    Fetch options chain data for a given ticker.

    Args:
        ticker_symbol: US stock ticker (e.g. 'AAPL', 'SPY')
        num_expirations: Number of expiration dates to fetch (default: 3, nearest)

    Returns:
        dict with stock info and options data
    """
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info or {}

    # Current stock price
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    if not current_price:
        # Try to get from history
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = round(float(hist["Close"].iloc[-1]), 2)

    # Available expiration dates
    expirations = ticker.options
    if not expirations:
        return {
            "error": f"No options data available for {ticker_symbol}",
            "ticker": ticker_symbol,
        }

    # Take nearest N expirations
    target_expirations = expirations[:num_expirations]

    result = {
        "ticker": ticker_symbol.upper(),
        "company_name": info.get("longName", info.get("shortName", "")),
        "current_price": current_price,
        "fetch_time": datetime.now().isoformat(),
        "expirations": [],
        "stock_info": {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "avg_volume": info.get("averageVolume"),
            "beta": info.get("beta"),
            "dividend_yield": info.get("dividendYield"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "pe_ratio": info.get("trailingPE"),
        },
    }

    for exp_date in target_expirations:
        try:
            chain = ticker.option_chain(exp_date)
            calls = chain.calls
            puts = chain.puts

            exp_result = {
                "expiration": exp_date,
                "days_to_expiry": (datetime.strptime(exp_date, "%Y-%m-%d") - datetime.now()).days,
                "calls": [],
                "puts": [],
                "summary": {},
            }

            # Process calls
            for _, row in calls.iterrows():
                exp_result["calls"].append({
                    "strike": float(row["strike"]),
                    "last_price": float(row["lastPrice"]),
                    "bid": float(row["bid"]) if pd.notna(row["bid"]) else None,
                    "ask": float(row["ask"]) if pd.notna(row["ask"]) else None,
                    "volume": int(row["volume"]) if pd.notna(row["volume"]) else 0,
                    "open_interest": int(row["openInterest"]) if pd.notna(row["openInterest"]) else 0,
                    "implied_volatility": float(row["impliedVolatility"]) if pd.notna(row["impliedVolatility"]) else None,
                    "in_the_money": bool(row["inTheMoney"]),
                    "change": float(row["change"]) if pd.notna(row["change"]) else None,
                    "percent_change": float(row["percentChange"]) if pd.notna(row["percentChange"]) else None,
                })

            # Process puts
            for _, row in puts.iterrows():
                exp_result["puts"].append({
                    "strike": float(row["strike"]),
                    "last_price": float(row["lastPrice"]),
                    "bid": float(row["bid"]) if pd.notna(row["bid"]) else None,
                    "ask": float(row["ask"]) if pd.notna(row["ask"]) else None,
                    "volume": int(row["volume"]) if pd.notna(row["volume"]) else 0,
                    "open_interest": int(row["openInterest"]) if pd.notna(row["openInterest"]) else 0,
                    "implied_volatility": float(row["impliedVolatility"]) if pd.notna(row["impliedVolatility"]) else None,
                    "in_the_money": bool(row["inTheMoney"]),
                    "change": float(row["change"]) if pd.notna(row["change"]) else None,
                    "percent_change": float(row["percentChange"]) if pd.notna(row["percentChange"]) else None,
                })

            # Compute summary statistics
            exp_result["summary"] = compute_summary(exp_result["calls"], exp_result["puts"], current_price)
            result["expirations"].append(exp_result)

        except Exception as e:
            result["expirations"].append({
                "expiration": exp_date,
                "error": str(e),
            })

    return result


def compute_summary(calls, puts, current_price):
    """Compute summary statistics for an expiration."""
    if not calls or not puts:
        return {}

    atm_strike = min(calls, key=lambda x: abs(x["strike"] - current_price))["strike"]

    # Filter to ATM and nearby strikes (±20%)
    nearby_calls = [c for c in calls if 0.8 * current_price <= c["strike"] <= 1.2 * current_price]
    nearby_puts = [p for p in puts if 0.8 * current_price <= p["strike"] <= 1.2 * current_price]

    # Total volume and open interest
    call_volume = sum(c["volume"] for c in calls)
    put_volume = sum(p["volume"] for p in puts)
    call_oi = sum(c["open_interest"] for c in calls)
    put_oi = sum(p["open_interest"] for p in puts)

    # Put/Call ratios
    pc_volume_ratio = round(put_volume / call_volume, 2) if call_volume > 0 else None
    pc_oi_ratio = round(put_oi / call_oi, 2) if call_oi > 0 else None

    # Average implied volatility
    avg_iv_calls = sum(c["implied_volatility"] for c in nearby_calls if c["implied_volatility"]) / max(len([c for c in nearby_calls if c["implied_volatility"]]), 1)
    avg_iv_puts = sum(p["implied_volatility"] for p in nearby_puts if p["implied_volatility"]) / max(len([p for p in nearby_puts if p["implied_volatility"]]), 1)
    avg_iv = round((avg_iv_calls + avg_iv_puts) / 2, 4)

    # Skew: difference between OTM put IV and OTM call IV
    otm_puts = [p for p in puts if p["strike"] < current_price and p["implied_volatility"]]
    otm_calls = [c for c in calls if c["strike"] > current_price and c["implied_volatility"]]
    put_iv_skew = sum(p["implied_volatility"] for p in otm_puts) / max(len(otm_puts), 1) if otm_puts else 0
    call_iv_skew = sum(c["implied_volatility"] for c in otm_calls) / max(len(otm_calls), 1) if otm_calls else 0
    iv_skew = round(put_iv_skew - call_iv_skew, 4)

    return {
        "atm_strike": atm_strike,
        "current_price_vs_atm": round(current_price - atm_strike, 2),
        "call_volume": call_volume,
        "put_volume": put_volume,
        "call_open_interest": call_oi,
        "put_open_interest": put_oi,
        "pc_volume_ratio": pc_volume_ratio,
        "pc_oi_ratio": pc_oi_ratio,
        "avg_implied_volatility": avg_iv,
        "iv_skew": iv_skew,
        "num_available_strikes": len(calls),
    }


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    num_exp = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    data = fetch_options(ticker, num_exp)
    print(json.dumps(data, indent=2, default=str))