# Options Strategies Reference

## Single-Leg Strategies

### Long Call
- **Direction**: Bullish
- **Risk**: Limited (premium paid)
- **Profit**: Unlimited (stock can rise indefinitely)
- **When**: Strong bullish outlook, low IV preferred
- **Max Loss**: Premium paid

### Long Put
- **Direction**: Bearish
- **Risk**: Limited (premium paid)
- **Profit**: Large (stock can fall to zero)
- **When**: Strong bearish outlook, hedge against downside
- **Max Loss**: Premium paid

### Short Put (Cash-Secured Put)
- **Direction**: Bullish / Neutral
- **Risk**: Large (stock can fall to zero)
- **Profit**: Limited (premium received)
- **When**: Collect premium, willing to buy stock at lower price
- **Max Loss**: Strike price - premium (if assigned)

### Short Call (Naked Call)
- **Direction**: Bearish / Neutral
- **Risk**: Unlimited (stock can rise indefinitely)
- **Profit**: Limited (premium received)
- **When**: Rarely recommended — use bear call spread instead
- **Max Loss**: Unlimited

## Spread Strategies (Two Legs)

### Bull Call Spread (Debit Spread)
- **Structure**: Buy lower strike call + Sell higher strike call (same expiry)
- **Direction**: Moderately bullish
- **Risk**: Limited (net debit paid)
- **Profit**: Limited (strike width - net debit)
- **When**: Bullish with defined risk, lower cost than naked call

### Bear Put Spread (Debit Spread)
- **Structure**: Buy higher strike put + Sell lower strike put (same expiry)
- **Direction**: Moderately bearish
- **Risk**: Limited (net debit paid)
- **Profit**: Limited (strike width - net debit)
- **When**: Bearish with defined risk

### Bull Put Spread (Credit Spread)
- **Structure**: Sell higher strike put + Buy lower strike put (same expiry)
- **Direction**: Bullish / Neutral
- **Risk**: Limited (strike width - credit)
- **Profit**: Limited (net credit received)
- **When**: High IV, bullish outlook, theta decay works in your favor

### Bear Call Spread (Credit Spread)
- **Structure**: Sell lower strike call + Buy higher strike call (same expiry)
- **Direction**: Bearish / Neutral
- **Risk**: Limited (strike width - credit)
- **Profit**: Limited (net credit received)
- **When**: High IV, bearish outlook, theta decay works in your favor

## Multi-Leg Strategies

### Iron Condor
- **Structure**: Bull Put Spread + Bear Call Spread (same expiry)
  - Sell OTM put + Buy further OTM put
  - Sell OTM call + Buy further OTM call
- **Direction**: Neutral (range-bound)
- **Risk**: Limited (width of widest wing)
- **Profit**: Limited (net credit received)
- **When**: High IV, expecting stock to stay within a range
- **Max Win Zone**: Between the two short strikes

### Long Straddle
- **Structure**: Buy ATM call + Buy ATM put (same expiry)
- **Direction**: Volatile (big move expected either way)
- **Risk**: Limited (combined premium paid)
- **Profit**: Unlimited (upside) or large (downside)
- **When**: Low IV, expecting big move but unsure of direction
- **Breakeven**: Strike ± combined premium

### Long Strangle
- **Structure**: Buy OTM call + Buy OTM put (same expiry)
- **Direction**: Volatile (big move expected)
- **Risk**: Limited (combined premium paid)
- **Profit**: Potentially large
- **When**: Cheaper than straddle, needs bigger move to profit
- **Breakeven**: Short put strike - premium, Short call strike + premium

### Short Straddle / Strangle
- **Structure**: Sell ATM call + Sell ATM put (same expiry)
- **Direction**: Neutral (low volatility expected)
- **Risk**: High (unlimited on upside, large on downside)
- **Profit**: Limited (premium collected)
- **When**: Extremely high IV, expecting IV crush and range-bound movement
- **Note**: High risk — consider Iron Condor instead for defined risk

## Time-Based Strategies

### Calendar Spread (Time Spread)
- **Structure**: Sell short-term option + Buy longer-term option (same strike)
- **Direction**: Neutral
- **Risk**: Limited (net debit)
- **Profit**: Varies (benefits from time decay of short option)
- **When**: Normal IV, neutral outlook, theta decay in near-term

### Diagonal Spread
- **Structure**: Sell short-term OTM option + Buy longer-term further OTM option
- **Direction**: Directional or neutral (varies by setup)
- **Risk**: Limited (net debit)
- **Profit**: Varies
- **When**: Combination of time decay and directional bias

## Income Strategies

### Covered Call (Buy-Write)
- **Structure**: Own 100 shares + Sell 1 OTM call
- **Direction**: Neutral / Slightly bullish
- **Risk**: Full stock value (downside)
- **Profit**: Premium + stock appreciation up to strike
- **When**: Own the stock, generate income, willing to sell at strike

### Wheel Strategy
- **Structure**: Cash-Secured Put → if assigned → Covered Call
- **Direction**: Neutral / Bullish
- **Risk**: Full stock value (if assigned and stock drops)
- **Profit**: Premiums collected
- **When**: Long-term income generation on stocks you want to own

---

## Key Metrics

| Metric | What It Tells You |
|--------|-------------------|
| **Implied Volatility (IV)** | Market's expected price movement. High IV = expensive options |
| **IV Skew** | Difference in IV between OTM puts and calls. Fear indicator |
| **Put/Call Ratio** | Volume: short-term sentiment. OI: longer-term positioning |
| **Open Interest** | Number of outstanding contracts. Liquidity indicator |
| **Volume** | Today's trading activity. Fresh money at work |
| **Theta** | Time decay. Works against long options, for short options |
| **Delta** | Sensitivity to stock price movement. Roughly = probability of ITM |
| **Gamma** | Rate of change of delta. High near expiration |

## Educational Disclaimer

**This reference is for educational purposes only.** Options trading carries significant risk. Strategies should be evaluated based on your individual financial situation, risk tolerance, and investment objectives. Consult a qualified financial advisor before making trading decisions.

---

## 达尔文投资哲学视角 (Darwinian Perspective)

This reference is enhanced by the philosophy from **"Investment Lessons from Darwin"** by Pulak Prasad (Nalada Capital).

### 达尔文核心原则 (Core Principles)

| Principle | Biology Analogy | Options Application |
|-----------|----------------|-------------------|
| **Type I Error** | Deer avoids predators | Avoid bad trades. "Don't Trade" is a win. |
| **ROCE as Filter** | Silver fox tameness → all traits | Quality stocks → better options outcomes |
| **Robustness** | DNA/Protein multi-layered stability | Iron Condors, Credit Spreads survive multiple scenarios |
| **Proximate vs Ultimate** | Short-term noise vs long-term fitness | Ignore daily noise, focus on business quality |
| **Convergent Patterns** | Same solutions in similar environments | Same strategies work for quality stocks globally |
| **Costly Signals** | Peacock's tail — expensive = honest | Volume + OI + IV > News + hype |
| **Punctuated Equilibrium** | Long stasis, rare change | Most days: do nothing. Wait for dislocations |
| **Compound Interest** | 1% advantage → 90% in 3000 generations | Small premium edges → large wealth over decades |

### 达尔文策略优先级 (Strategy Priority)

```
1st Priority:  INCOME STRATEGIES (Cash-Secured Put, Covered Call)
   → Compound returns over time, like Darwin's rabbits

2nd Priority:  CREDIT SPREADS (Bull Put, Bear Call, Iron Condor)
   → Sell premium during high IV, be the insurance company

3rd Priority:  DEBIT SPREADS (Bull Call, Bear Put)
   → Defined risk, limited profit, use sparingly

4th Priority:  DIRECTIONAL (Long Call, Long Put)
   → Only for exceptional quality, small position size

Last Priority:  DON'T TRADE
   → Most of the time, this is the best option
```

### 案例: 达尔文 vs 常规分析

**Conventional approach:**
- Check sentiment → neutral
- Check IV → normal
- Recommend strategies → Calendar Spread, Covered Call

**Darwinian approach (this skill):**
- Assess business quality → **Exceptional** (high ROCE, no debt, stable industry)
- Check punctuated equilibrium → **None detected** (normal market)
- **Primary**: Cash-Secured Put (income on quality)
- **Secondary**: Covered Call (compound returns)
- **Rationale**: "Quality business, normal conditions — wait for punctuation or sell premium"

### 何时不交易 (When NOT to Trade)

The Darwinian approach actively recommends **NOT trading**:

1. **Poor quality stock** → 🚫 Don't trade options on it
2. **No punctuation event** → ⏸️ Wait for dislocation
3. **Complacency** (all-time high + low IV) → ⚠️ Danger zone
4. **Fast-changing industry** → 🚫 Avoid (tech, crypto, biotech hype)
5. **High leverage company** → 🚫 Avoid (bankruptcy risk)
6. **Turnaround story** → 🚫 Avoid (most fail, per Darwinian evidence)

> "The best investors are the best rejectors." — Pulak Prasad