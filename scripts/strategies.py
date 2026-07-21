#!/usr/bin/env python3
"""
Options Strategy Recommender
Inspired by "Investment Lessons from Darwin" by Pulak Prasad

Integrates Darwinian investment philosophy (Nalada Capital approach):
1. Type I error avoidance first — the best investors are the best rejectors
2. Only trade options on high-quality businesses (ROCE filter, robustness)
3. Use punctuated equilibrium — market dislocations create the best opportunities
4. Compound over time with income strategies — be the bee, not the butterfly
5. Trust costly signals (volume, OI, IV) not cheap signals (news, hype)
"""

import json
import sys
from enum import Enum
from datetime import datetime


class Sentiment(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    SLIGHTLY_BULLISH = "slightly_bullish"
    SLIGHTLY_BEARISH = "slightly_bearish"


class Volatility(Enum):
    HIGH = "high"
    LOW = "low"
    NORMAL = "normal"


class DarwinianQuality(Enum):
    """Darwin-inspired business quality assessment."""
    EXCEPTIONAL = "exceptional"       # High ROCE, zero debt, wide moat, stable industry
    GOOD = "good"                     # Good ROCE, low debt, decent moat
    AVERAGE = "average"               # Moderate metrics, some red flags
    POOR = "poor"                     # Low ROCE, high debt, no moat, fast-changing industry
    SPECULATIVE = "speculative"       # No earnings, negative cash flow, hype-driven


class StrategyRecommendation:
    def __init__(
        self,
        name: str,
        direction: str,
        risk_level: str,
        max_profit: str,
        max_loss: str,
        description: str,
        when_to_use: str,
        darwinian_rationale: str,  # Darwinian philosophy justification
        probability: float,
        recommended: bool = True,  # False means "avoid this" (Type I error prevention)
        suggested_strikes: list = None,
    ):
        self.name = name
        self.direction = direction
        self.risk_level = risk_level
        self.max_profit = max_profit
        self.max_loss = max_loss
        self.description = description
        self.when_to_use = when_to_use
        self.darwinian_rationale = darwinian_rationale
        self.probability = probability
        self.recommended = recommended
        self.suggested_strikes = suggested_strikes or []

    def to_dict(self):
        return {
            "name": self.name,
            "direction": self.direction,
            "risk_level": self.risk_level,
            "max_profit": self.max_profit,
            "max_loss": self.max_loss,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "darwinian_rationale": self.darwinian_rationale,
            "score": round(self.probability, 2),
            "recommended": self.recommended,
            "suggested_strikes": self.suggested_strikes,
        }


# ============================================================
# DARWINIAN QUALITY ASSESSMENT
# ============================================================

def assess_darwinian_quality(data: dict) -> tuple:
    """
    Assess the underlying stock's business quality using Darwinian principles.
    
    Returns (DarwinianQuality, score, details).
    
    Based on Pulak Prasad's framework:
    - High ROCE = the single filter (like silver fox tameness)
    - Low/zero debt = robustness
    - Stable industry = punctuated equilibrium
    - Strong moat = competitive advantage
    """
    info = data.get("stock_info", {}) or {}
    score = 0.0
    reasons = []

    # 1. ROCE proxy: ROE / operating margins / profitability
    pe_ratio = info.get("pe_ratio")
    if pe_ratio and pe_ratio > 0:
        # Low PE for high-quality = good value; but quality ≠ value
        pass

    # 2. Debt assessment (零杠杆 = 达尔文稳健性)
    beta = info.get("beta")
    if beta is not None:
        if beta < 0.8:
            score += 0.15
            reasons.append("Low beta suggests stable business (robustness)")
        elif beta > 1.5:
            score -= 0.2
            reasons.append("High beta — high volatility, low robustness")

    # 3. Dividend yield (cash generation ability)
    div_yield = info.get("dividend_yield")
    if div_yield is not None:
        if div_yield > 0.02:
            score += 0.15
            reasons.append("Pays dividend — generates real cash")
        elif div_yield == 0:
            score -= 0.05
            reasons.append("No dividend — may not generate free cash flow")

    # 4. Industry stability (avoid fast-changing industries)
    sector = (info.get("sector") or "").lower()
    stable_sectors = [
        "consumer", "defensive", "utilities", "healthcare", "energy",
        "industrials", "basic materials", "financial services", "insurance"
    ]
    fast_sectors = [
        "technology", "communication", "semiconductor", "biotechnology",
        "internet", "software", "electric vehicle", "cannabis", "crypto"
    ]
    is_stable = any(s in sector for s in stable_sectors)
    is_fast = any(s in sector for s in fast_sectors)

    if is_stable and not is_fast:
        score += 0.25
        reasons.append(f"Sector ({sector}) is stable — business stagnation is normal")
    elif is_fast:
        score -= 0.3
        reasons.append(f"Sector ({sector}) is fast-changing — avoid, per Darwinian principle")

    # 5. Market cap (size = robustness)
    mcap = info.get("market_cap")
    if mcap:
        if mcap > 50e9:  # > $50B
            score += 0.2
            reasons.append("Large cap (>$50B) — multi-layered robustness")
        elif mcap > 10e9:
            score += 0.1
            reasons.append("Mid-large cap — some robustness")
        elif mcap < 1e9:
            score -= 0.15
            reasons.append("Small cap — lacks robustness buffer")

    # 6. 52-week range (punctuated equilibrium indicator)
    high = info.get("fifty_two_week_high")
    low = info.get("fifty_two_week_low")
    current = data.get("current_price")
    if high and low and current:
        if current < low * 1.15:  # Near 52-week low
            score += 0.15
            reasons.append("Near 52-week low — potential punctuated equilibrium buying opportunity")
        elif current > high * 0.85:  # Near 52-week high
            score -= 0.05
            reasons.append("Near 52-week high — may be overvalued")

    # Classify
    if score >= 0.5:
        return DarwinianQuality.EXCEPTIONAL, score, reasons
    elif score >= 0.2:
        return DarwinianQuality.GOOD, score, reasons
    elif score >= -0.1:
        return DarwinianQuality.AVERAGE, score, reasons
    elif score >= -0.3:
        return DarwinianQuality.POOR, score, reasons
    else:
        return DarwinianQuality.SPECULATIVE, score, reasons


# ============================================================
# PUNCTUATED EQUILIBRIUM DETECTOR
# ============================================================

def detect_punctuated_equilibrium(data: dict) -> dict:
    """
    Detect market dislocations (punctuated equilibrium events).
    
    From the book: the best buying opportunities come during
    "punctuations" — rare, sharp market dislocations.
    """
    result = {
        "is_punctuation": False,
        "type": "none",
        "description": "Normal market conditions — no punctuated equilibrium detected.",
        "darwinian_advice": "Most of the time, the best action is no action. Be patient.",
    }

    info = data.get("stock_info", {}) or {}
    current_price = data.get("current_price")
    high = info.get("fifty_two_week_high")
    low = info.get("fifty_two_week_low")

    if not current_price or not high or not low:
        return result

    # Check for IV spike (fear/punctuation)
    ivs = []
    for exp in data.get("expirations", []):
        iv = exp.get("summary", {}).get("avg_implied_volatility")
        if iv:
            ivs.append(iv)

    avg_iv = sum(ivs) / len(ivs) if ivs else 0

    # Punctuation: stock near 52-week low AND high IV
    if current_price <= low * 1.10 and avg_iv > 0.4:
        result["is_punctuation"] = True
        result["type"] = "fear_punctuation"
        result["description"] = (
            f"⚠️ PUNCTUATED EQUILIBRIUM DETECTED: Stock near 52-week low "
            f"({current_price:.2f} vs low {low:.2f}) with elevated IV ({avg_iv:.1%}). "
            f"This is a rare buying opportunity — like the 2008/2020 dislocations."
        )
        result["darwinian_advice"] = (
            "This is a 'punctuation' event. As Pulak Prasad teaches: "
            "use rare discontinuities to buy, not sell. The best investors "
            "are patient and strike when others panic. Consider selling puts "
            "(cash-secured or credit spreads) to collect rich premium."
        )

    # Punctuation: extremely high IV without price crash (IV spike)
    elif avg_iv > 0.6:
        result["is_punctuation"] = True
        result["type"] = "iv_spike"
        result["description"] = (
            f"⚠️ IV SPIKE DETECTED: Implied volatility is {avg_iv:.1%}. "
            f"Premium sellers are richly rewarded. Like the Darwinian principle: "
            f"when everyone is fearful, be greedy (within reason)."
        )
        result["darwinian_advice"] = (
            "High IV environment favors premium selling strategies "
            "(Iron Condor, Credit Spreads, Cash-Secured Puts). "
            "Avoid buying options — premiums are too expensive."
        )

    # Punctuation: stock near 52-week high with low IV (complacency)
    elif current_price >= high * 0.95 and avg_iv < 0.2:
        result["is_punctuation"] = True
        result["type"] = "complacency"
        result["description"] = (
            f"⚠️ COMPLACENCY DETECTED: Stock near all-time high with low IV ({avg_iv:.1%}). "
            f"Markets are complacent — like the calm before the storm."
        )
        result["darwinian_advice"] = (
            "Low IV + high prices = danger zone. The Darwinian lesson: "
            "avoid Type I errors. Consider protective puts or reduce exposure. "
            "Do not chase momentum."
        )

    return result


def classify_sentiment(data: dict) -> tuple:
    """Classify market sentiment from options data. (Unchanged from original)"""
    sentiment_scores = []

    for exp in data.get("expirations", []):
        summary = exp.get("summary", {})

        pc_vol = summary.get("pc_volume_ratio")
        if pc_vol is not None:
            if pc_vol > 1.3:
                sentiment_scores.append(("bearish", -0.8))
            elif pc_vol > 1.0:
                sentiment_scores.append(("bearish", -0.3))
            elif pc_vol < 0.5:
                sentiment_scores.append(("bullish", 0.8))
            elif pc_vol < 0.7:
                sentiment_scores.append(("bullish", 0.4))
            else:
                sentiment_scores.append(("neutral", 0.0))

        pc_oi = summary.get("pc_oi_ratio")
        if pc_oi is not None:
            if pc_oi > 1.3:
                sentiment_scores.append(("bearish", -0.6))
            elif pc_oi < 0.6:
                sentiment_scores.append(("bullish", 0.6))
            else:
                sentiment_scores.append(("neutral", 0.0))

        iv_skew = summary.get("iv_skew")
        if iv_skew is not None:
            if iv_skew > 0.05:
                sentiment_scores.append(("bearish", -0.5))
            elif iv_skew < -0.05:
                sentiment_scores.append(("bullish", 0.5))

    if not sentiment_scores:
        return Sentiment.NEUTRAL, 0.0

    total_score = sum(s[1] for s in sentiment_scores)
    avg_score = total_score / len(sentiment_scores)

    if avg_score > 0.5:
        return Sentiment.BULLISH, avg_score
    elif avg_score > 0.15:
        return Sentiment.SLIGHTLY_BULLISH, avg_score
    elif avg_score < -0.5:
        return Sentiment.BEARISH, abs(avg_score)
    elif avg_score < -0.15:
        return Sentiment.SLIGHTLY_BEARISH, abs(avg_score)
    else:
        return Sentiment.NEUTRAL, abs(avg_score)


def classify_volatility(data: dict) -> tuple:
    """Classify implied volatility regime. (Unchanged from original)"""
    ivs = []
    for exp in data.get("expirations", []):
        iv = exp.get("summary", {}).get("avg_implied_volatility")
        if iv:
            ivs.append(iv)

    if not ivs:
        return Volatility.NORMAL, 0.0

    avg_iv = sum(ivs) / len(ivs)

    if avg_iv > 0.5:
        return Volatility.HIGH, avg_iv
    elif avg_iv < 0.2:
        return Volatility.LOW, avg_iv
    else:
        return Volatility.NORMAL, avg_iv


def find_liquid_strikes(contracts, current_price, count=3):
    """Find the most liquid strikes near the money."""
    if not contracts:
        return []

    nearby = [c for c in contracts if 0.85 * current_price <= c["strike"] <= 1.15 * current_price]
    nearby.sort(key=lambda c: (c["volume"] + c["open_interest"]), reverse=True)
    return nearby[:count]


# ============================================================
# DARWINIAN STRATEGY RECOMMENDATION ENGINE
# ============================================================

def recommend_strategies(data: dict) -> list:
    """
    Main recommendation engine integrating Darwinian philosophy.
    
    Key principles from Pulak Prasad's "Investment Lessons from Darwin":
    1. TYPE I ERROR FIRST: Most important decision is what NOT to do
    2. QUALITY MATTERS: Only trade options on high-quality businesses
    3. PUNCTUATED EQUILIBRIUM: Rare dislocations = best opportunities
    4. COMPOUND OVER TIME: Prefer income strategies for steady compounding
    5. BE THE BEE: Simple, repeatable process beats complex predictions
    """
    sentiment, confidence = classify_sentiment(data)
    vol_regime, avg_iv = classify_volatility(data)
    darwin_quality, quality_score, quality_reasons = assess_darwinian_quality(data)
    punctuation = detect_punctuated_equilibrium(data)

    current_price = data.get("current_price")
    recommendations = []
    warnings = []

    if not current_price:
        return [{"error": "No current price data available"}]

    nearest_exp = data.get("expirations", [{}])[0]
    if not nearest_exp or "error" in nearest_exp:
        return [{"error": "No valid expiration data"}]

    calls = nearest_exp.get("calls", [])
    puts = nearest_exp.get("puts", [])
    days_to_expiry = nearest_exp.get("days_to_expiry", 30)
    expiry = nearest_exp.get("expiration", "N/A")

    # ============================================================
    # DARWINIAN PRINCIPLE 1: TYPE I ERROR AVOIDANCE
    # The best investors are the best rejectors.
    # ============================================================

    if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
        warnings.append(
            f"⚠️ DARWINIAN ALERT: '{data.get('ticker')}' scores {darwin_quality.value} "
            f"on business quality ({quality_score:.2f}). Per Pulak Prasad's first principle: "
            f"AVOID. The best investors are the best rejectors. "
            f"Type I error (bad investment) is far more dangerous than Type II error (missing out)."
        )

    if darwin_quality == DarwinianQuality.AVERAGE and punctuation["is_punctuation"]:
        warnings.append(
            f"⚠️ CAUTION: Average quality stock ({data.get('ticker')}) with "
            f"punctuated equilibrium event. Only consider income strategies "
            f"(selling premium) with tight risk controls. "
            f"Darwinian lesson: don't confuse price volatility with business discontinuity."
        )

    # ============================================================
    # DARWINIAN PRINCIPLE 2: PUNCTUATED EQUILIBRIUM
    # Use rare dislocations to buy, not sell.
    # ============================================================

    if punctuation["is_punctuation"]:
        recommendations.append(StrategyRecommendation(
            name=f"Punctuated Equilibrium: {punctuation['type'].replace('_', ' ').title()}",
            direction="strategic",
            risk_level="varies",
            max_profit="Varies by strategy",
            max_loss="Varies by strategy",
            description=punctuation["description"],
            when_to_use=punctuation["darwinian_advice"],
            darwinian_rationale="Pulak Prasad: 'Use rare discontinuities to buy, not sell. "
                                "The best investors are patient and strike when others panic.' "
                                "Like the Nalada Capital approach during 2008 and 2020.",
            probability=0.85 if punctuation["type"] == "fear_punctuation" else 0.70,
            recommended=True,
        ))

    # ============================================================
    # DARWINIAN PRINCIPLE 3: INCOME STRATEGIES (COMPOUNDING)
    # Like Darwin's insight on compound interest — small edges
    # compounded over time produce extraordinary results.
    # ============================================================

    # Cash-Secured Put (达尔文收入策略 #1)
    # Nalada: "We want to become permanent owners of high-quality businesses."
    # Cash-secured puts = getting paid to wait to buy quality at a discount.
    if puts and current_price:
        otm_put = [p for p in puts if 0.85 * current_price <= p["strike"] <= 0.97 * current_price]
        if otm_put:
            liquid_put = sorted(otm_put, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[0]
            score = 0.70
            if darwin_quality in (DarwinianQuality.EXCEPTIONAL, DarwinianQuality.GOOD):
                score = 0.80  # Higher quality = higher confidence
            elif darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                score = 0.30  # Low quality = avoid

            recommendations.append(StrategyRecommendation(
                name="Cash-Secured Put (达尔文收入策略)",
                direction="neutral/bullish",
                risk_level="low",
                max_profit="Premium received",
                max_loss=f"Strike price (${liquid_put['strike']}) - premium, if assigned",
                description=f"Sell a put at ${liquid_put['strike']} to collect premium. "
                            f"Quality: {darwin_quality.value}. "
                            f"Willing to buy quality at a discount if assigned.",
                when_to_use="Income generation on quality businesses. "
                            "Darwinian: 'We want to become permanent owners of quality.' "
                            "Getting paid to wait for a good entry price.",
                darwinian_rationale="Pulak Prasad: 'We use the unavoidable short-term "
                                    "fluctuations of quality businesses to buy, not sell.' "
                                    "Cash-secured puts = getting paid to wait for a punctuation event.",
                probability=score,
                recommended=score >= 0.50,
                suggested_strikes=[liquid_put["strike"]],
            ))

    # Covered Call (达尔文收入策略 #2)
    # Compound income from existing holdings — like Nalada's "permanent owner" philosophy
    if calls and current_price:
        otm_call = [c for c in calls if 1.02 * current_price <= c["strike"] <= 1.15 * current_price]
        if otm_call:
            liquid_call = sorted(otm_call, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[0]
            score = 0.65
            if darwin_quality in (DarwinianQuality.EXCEPTIONAL, DarwinianQuality.GOOD):
                score = 0.75
            elif darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                score = 0.25

            recommendations.append(StrategyRecommendation(
                name="Covered Call (达尔文收入策略)",
                direction="neutral/bullish",
                risk_level="low",
                max_profit=f"Premium + stock appreciation up to ${liquid_call['strike']}",
                max_loss="Full stock value (if stock drops to zero)",
                description=f"Own the stock, sell a call at ${liquid_call['strike']}. "
                            f"Generate income while holding quality. "
                            f"Quality: {darwin_quality.value}.",
                when_to_use="Already own the stock, neutral-to-slightly bullish outlook. "
                            "Darwinian: 'Be the permanent owner who generates income.' "
                            "Compound returns over time.",
                darwinian_rationale="Pulak Prasad: 'If you own a quality business, "
                                    "why sell it? Compound returns over decades.' "
                                    "Covered calls let you generate income while holding.",
                probability=score,
                recommended=score >= 0.50,
                suggested_strikes=[liquid_call["strike"]],
            ))

    # ============================================================
    # DARWINIAN PRINCIPLE 4: STRATEGY MATCHING
    # Based on sentiment + volatility + quality
    # ============================================================

    # --- Bullish strategies ---
    if sentiment in (Sentiment.BULLISH, Sentiment.SLIGHTLY_BULLISH):

        # Bull Put Spread (Credit Spread) — preferred for high IV
        if vol_regime == Volatility.HIGH:
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.95]
            if otm_puts:
                liquid_puts = sorted(otm_puts, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[:2]
                strike = liquid_puts[0]["strike"] if liquid_puts else round(current_price * 0.93, 2)
                score = 0.75
                if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                    score = 0.30

                recommendations.append(StrategyRecommendation(
                    name="Bull Put Spread (Credit Spread)",
                    direction="bullish",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of strikes - net credit",
                    description=f"Sell a put at ${strike} and buy a lower put as protection. "
                                f"IV is high ({avg_iv:.1%}), so premiums are rich. "
                                f"Quality: {darwin_quality.value}.",
                    when_to_use="High IV + bullish outlook. Theta works in your favor. "
                                "Darwinian: 'When IV is high, sell premium — nature abhors a vacuum.'",
                    darwinian_rationale="Pulak Prasad: 'High quality businesses with high volatility "
                                        "create the best risk/reward. The market overreacts.' "
                                        "Selling put credit spreads = being the insurance company.",
                    probability=score,
                    recommended=score >= 0.50,
                    suggested_strikes=[strike, round(strike - 0.05 * current_price, 2)],
                ))

        # Long Call — only for exceptional quality businesses
        if vol_regime in (Volatility.LOW, Volatility.NORMAL):
            otm_calls_1 = [c for c in calls if c["strike"] > current_price * 1.02]
            if otm_calls_1:
                liquid_calls = sorted(otm_calls_1, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[:2]
                strike = liquid_calls[0]["strike"] if liquid_calls else round(current_price * 1.05, 2)
                score = 0.35
                if darwin_quality == DarwinianQuality.EXCEPTIONAL:
                    score = 0.45
                elif darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                    score = 0.10

                recommendations.append(StrategyRecommendation(
                    name="Long Call",
                    direction="bullish",
                    risk_level="high",
                    max_profit="Unlimited",
                    max_loss=f"Premium paid (${strike} strike)",
                    description=f"Buy a call option at ${strike}. "
                                f"Confidence: {confidence:.0%}. Quality: {darwin_quality.value}.",
                    when_to_use="Strong bullish outlook on a quality business, low IV. "
                                "Darwinian: 'Small bets on quality during low IV are acceptable.' "
                                "But prepare for Type I error (total loss of premium).",
                    darwinian_rationale="Pulak Prasad: 'We accept Type II errors (missing Tesla) "
                                        "to avoid Type I errors (losing capital).' "
                                        "Long calls are high-risk — only on exceptional quality.",
                    probability=score,
                    recommended=score >= 0.40 and darwin_quality in (DarwinianQuality.EXCEPTIONAL, DarwinianQuality.GOOD),
                    suggested_strikes=[strike],
                ))

        # Bull Call Spread — limited risk, moderate reward
        otm_calls = [c for c in calls if c["strike"] > current_price * 1.02]
        if len(otm_calls) >= 2:
            lower_strike = otm_calls[0]["strike"]
            higher_strike = otm_calls[min(2, len(otm_calls) - 1)]["strike"]
            score = 0.45
            if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                score = 0.20

            recommendations.append(StrategyRecommendation(
                name="Bull Call Spread (Debit Spread)",
                direction="bullish",
                risk_level="medium",
                max_profit="(Higher strike - lower strike) - net debit",
                max_loss="Net debit paid",
                description=f"Buy ${lower_strike} call, sell ${higher_strike} call. "
                            f"Limited risk, defined profit. Quality: {darwin_quality.value}.",
                when_to_use="Moderately bullish with defined risk. "
                            "Darwinian: 'Defined risk is the hallmark of a robust strategy.' "
                            "Smaller loss than a naked call if wrong.",
                darwinian_rationale="Pulak Prasad: 'Multi-layered robustness protects against the unexpected.' "
                                    "Bull call spreads = limited downside, capturing upside with bounded risk.",
                probability=score,
                recommended=score >= 0.40,
                suggested_strikes=[lower_strike, higher_strike],
            ))

    # --- Bearish strategies ---
    elif sentiment in (Sentiment.BEARISH, Sentiment.SLIGHTLY_BEARISH):

        # Bear Call Spread (Credit Spread) — preferred for high IV
        if vol_regime == Volatility.HIGH:
            otm_calls = [c for c in calls if c["strike"] > current_price * 1.05]
            if otm_calls:
                liquid_calls = sorted(otm_calls, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[:2]
                strike = liquid_calls[0]["strike"] if liquid_calls else round(current_price * 1.07, 2)
                score = 0.70
                if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                    score = 0.30

                recommendations.append(StrategyRecommendation(
                    name="Bear Call Spread (Credit Spread)",
                    direction="bearish",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of strikes - net credit",
                    description=f"Sell a call at ${strike} and buy a higher call as protection. "
                                f"IV is high ({avg_iv:.1%}), collect rich premium. "
                                f"Quality: {darwin_quality.value}.",
                    when_to_use="High IV, bearish outlook. Theta decay works in your favor. "
                                "Darwinian: 'Premium selling during high IV = evolutionary advantage.'",
                    darwinian_rationale="Pulak Prasad: 'When fear is high (elevated IV), "
                                        "be the seller of insurance. The market overpays for protection.'",
                    probability=score,
                    recommended=score >= 0.50,
                    suggested_strikes=[strike, round(strike + 0.05 * current_price, 2)],
                ))

        # Long Put — only for exceptional quality, as a hedge
        if vol_regime in (Volatility.LOW, Volatility.NORMAL):
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.98]
            if otm_puts:
                liquid_puts = sorted(otm_puts, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[:2]
                strike = liquid_puts[0]["strike"] if liquid_puts else round(current_price * 0.95, 2)
                score = 0.30

                recommendations.append(StrategyRecommendation(
                    name="Long Put (Hedge)",
                    direction="bearish",
                    risk_level="high",
                    max_profit="Large (up to strike price)",
                    max_loss=f"Premium paid (${strike} strike)",
                    description=f"Buy a put option at ${strike}. "
                                f"Confidence: {confidence:.0%}. Quality: {darwin_quality.value}. "
                                f"Best used as a hedge, not a speculation.",
                    when_to_use="Hedging against downside on a quality position. "
                                "Darwinian: 'Protective puts are like robust biological systems — "
                                "they provide multi-layered defense.' "
                                "Not for speculative short bets.",
                    darwinian_rationale="Pulak Prasad: 'We avoid predicting the future. "
                                        "Long puts are expensive and rarely profitable. "
                                        "Only use as portfolio insurance.'",
                    probability=score,
                    recommended=score >= 0.40,
                    suggested_strikes=[strike],
                ))

        # Bear Put Spread
        otm_puts_for_spread = [p for p in puts if p["strike"] < current_price * 0.98]
        if len(otm_puts_for_spread) >= 2:
            higher_strike = otm_puts_for_spread[0]["strike"]
            lower_strike = otm_puts_for_spread[min(1, len(otm_puts_for_spread) - 1)]["strike"]
            score = 0.40
            if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                score = 0.20

            recommendations.append(StrategyRecommendation(
                name="Bear Put Spread (Debit Spread)",
                direction="bearish",
                risk_level="medium",
                max_profit="(Higher strike - lower strike) - net debit",
                max_loss="Net debit paid",
                description=f"Buy ${higher_strike} put, sell ${lower_strike} put. "
                            f"Limited risk, defined profit. Quality: {darwin_quality.value}.",
                when_to_use="Moderately bearish with defined risk. "
                            "Darwinian: 'Bearish bets on quality businesses are usually wrong. "
                            "Quality businesses tend to recover.' Use sparingly.",
                darwinian_rationale="Pulak Prasad: 'Quality businesses compound over time. "
                                    "Betting against them is a Type I error waiting to happen.' "
                                    "Only consider for short-term tactical hedges.",
                probability=score,
                recommended=score >= 0.40,
                suggested_strikes=[higher_strike, lower_strike],
            ))

    # --- Neutral strategies ---
    else:
        if vol_regime == Volatility.HIGH:
            # Iron Condor — preferred neutral strategy for high IV
            otm_calls = [c for c in calls if c["strike"] > current_price * 1.08]
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.92]
            if otm_calls and otm_puts:
                call_strike = otm_calls[0]["strike"] if otm_calls else round(current_price * 1.10, 2)
                put_strike = otm_puts[-1]["strike"] if otm_puts else round(current_price * 0.90, 2)
                score = 0.65
                if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
                    score = 0.30

                recommendations.append(StrategyRecommendation(
                    name="Iron Condor (达尔文稳健策略)",
                    direction="neutral",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of a wing - net credit",
                    description=f"Sell ${put_strike} put / buy lower put + sell ${call_strike} call / buy higher call. "
                                f"IV is high ({avg_iv:.1%}) — perfect for selling premium. "
                                f"Quality: {darwin_quality.value}.",
                    when_to_use="Neutral outlook with high IV. "
                                "Darwinian: 'Robust strategies have multi-layered defenses. "
                                "Iron condors are the biological equivalent — "
                                "they profit from multiple scenarios.'",
                    darwinian_rationale="Pulak Prasad: 'Multi-layered robustness is the key to long-term survival. "
                                        "Iron condors are robust — they profit from range-bound movement, "
                                        "theta decay, and IV contraction.'",
                    probability=score,
                    recommended=score >= 0.50,
                    suggested_strikes=[put_strike, call_strike],
                ))

        elif vol_regime == Volatility.LOW:
            # Long Straddle — only during rare low IV on quality businesses
            atm_strike = nearest_exp.get("summary", {}).get("atm_strike", current_price)
            score = 0.25
            if darwin_quality == DarwinianQuality.EXCEPTIONAL and punctuation["is_punctuation"]:
                score = 0.40

            recommendations.append(StrategyRecommendation(
                name="Long Straddle",
                direction="neutral",
                risk_level="high",
                max_profit="Unlimited (on upside) or large (on downside)",
                max_loss="Combined premium paid",
                description=f"Buy ATM call + buy ATM put at ${atm_strike}. "
                            f"IV is low ({avg_iv:.1%}). Quality: {darwin_quality.value}.",
                when_to_use="Expecting a big move but unsure of direction. "
                            "Darwinian: 'Straddles are like punctuated equilibrium bets — "
                            "you're betting on a discontinuity. Low probability but high payoff.' "
                            "Only for exceptional quality businesses.",
                darwinian_rationale="Pulak Prasad: 'Most of the time, nothing happens. "
                                    "But occasionally, punctuations occur. "
                                    "Straddles during low IV are cheap bets on rare events.'",
                probability=score,
                recommended=score >= 0.35,
                suggested_strikes=[atm_strike],
            ))

        else:
            # Calendar Spread — neutral, normal IV, time decay
            recommendations.append(StrategyRecommendation(
                name="Calendar Spread (Time Spread)",
                direction="neutral",
                risk_level="low",
                max_profit="Varies (time decay of short option)",
                max_loss="Net debit paid",
                description=f"Sell a near-term ATM call at ${current_price}, buy a longer-term one. "
                            f"Profits from time decay. Quality: {darwin_quality.value}.",
                when_to_use="Neutral outlook, normal IV. "
                            "Darwinian: 'Calendar spreads benefit from the predictable passage of time. "
                            "Like compound interest — small, steady edge over time.'",
                darwinian_rationale="Pulak Prasad: 'Time is the friend of the quality business. "
                                    "Calendar spreads let you profit from theta decay — "
                                    "the most predictable force in options.'",
                probability=0.55,
                recommended=True,
                suggested_strikes=[current_price],
            ))

    # ============================================================
    # DARWINIAN PRINCIPLE 5: THE "DON'T TRADE" RECOMMENDATION
    # The best investors are the best rejectors.
    # ============================================================

    # Add a "Don't Trade" warning when conditions are unfavorable
    if darwin_quality in (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE):
        recommendations.append(StrategyRecommendation(
            name="🚫 DON'T TRADE (Type I Error Prevention)",
            direction="avoid",
            risk_level="N/A",
            max_profit="N/A (avoiding loss = profit)",
            max_loss="N/A",
            description=f"Business quality assessment: {darwin_quality.value} ({quality_score:.2f}). "
                        f"Per Pulak Prasad's Darwinian framework, this stock fails the quality test. "
                        f"Reasons: {'; '.join(quality_reasons[:3])}",
            when_to_use="Always — when the underlying business quality is poor. "
                        "Darwinian: 'The best investors are the best rejectors. "
                        "Type I errors (bad investments) destroy far more wealth "
                        "than Type II errors (missed opportunities).'",
            darwinian_rationale="Pulak Prasad, Chapter 1: 'Survival first. The six no-go zones: "
                                "fraudsters, turnarounds, high leverage, M&A addicts, "
                                "fast-changing industries, misaligned owners.' "
                                "This stock exhibits characteristics of these no-go zones.",
            probability=0.95,
            recommended=False,
        ))

    elif vol_regime == Volatility.NORMAL and not punctuation["is_punctuation"] and darwin_quality == DarwinianQuality.AVERAGE:
        recommendations.append(StrategyRecommendation(
            name="⏸️ WAIT (Punctuated Equilibrium Strategy)",
            direction="neutral",
            risk_level="N/A",
            max_profit="N/A",
            max_loss="N/A",
            description=f"Normal volatility, average quality, no punctuation event. "
                        f"The Darwinian principle: most of the time, the best action is no action. "
                        f"Wait for a punctuation event (market dislocation, IV spike, or price crash) "
                        f"before deploying capital.",
            when_to_use="When no clear edge exists. "
                        "Darwinian: 'Like the Nalada Capital approach — "
                        "they waited years between major investments. "
                        "Patience is a competitive advantage.'",
            darwinian_rationale="Pulak Prasad: 'In 14 years, 46% of capital was deployed "
                                "in just 26 months of punctuation events. "
                                "The rest of the time: wait. Be the bee — simple, repeatable, patient.'",
            probability=0.90,
            recommended=False,
        ))

    # ============================================================
    # FINAL: Sort by score, trim to top 7
    # ============================================================

    recommendations.sort(key=lambda r: r.probability, reverse=True)

    return {
        "ticker": data.get("ticker"),
        "company_name": data.get("company_name"),
        "current_price": current_price,
        "analysis_date": data.get("fetch_time", ""),
        "nearest_expiration": expiry,
        "days_to_expiry": days_to_expiry,
        "darwinian_quality": {
            "label": darwin_quality.value,
            "score": round(quality_score, 2),
            "details": quality_reasons,
        },
        "punctuated_equilibrium": punctuation,
        "sentiment": {
            "label": sentiment.value,
            "confidence": round(confidence, 2),
        },
        "volatility": {
            "label": vol_regime.value,
            "implied_volatility": round(avg_iv, 4) if isinstance(avg_iv, float) else avg_iv,
        },
        "warnings": warnings,
        "recommendations": [r.to_dict() for r in recommendations[:7]],
        "philosophy": "This analysis integrates 'Investment Lessons from Darwin' by Pulak Prasad. "
                       "Core principles: (1) Type I error avoidance — the best investors are the best "
                       "rejectors; (2) Quality matters — only trade options on high-quality businesses; "
                       "(3) Punctuated equilibrium — use rare dislocations, don't trade frequently; "
                       "(4) Compound over time — prefer income strategies; "
                       "(5) Be the bee — simple, repeatable process beats complex predictions.",
        "disclaimer": "This is for educational/informational purposes only. Not financial advice. "
                       "Options trading involves substantial risk. "
                       "As Darwin teaches: 'Survival first, profits second.' "
                       "Always do your own due diligence.",
    }


def main():
    """CLI entry point: read JSON from stdin or file, output recommendations."""
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    result = recommend_strategies(data)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()