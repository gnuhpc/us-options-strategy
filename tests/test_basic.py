#!/usr/bin/env python3
"""Basic tests for the options strategy scripts — Darwinian version."""

import json
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.strategies import (
    classify_sentiment,
    classify_volatility,
    Sentiment,
    Volatility,
    DarwinianQuality,
    assess_darwinian_quality,
    detect_punctuated_equilibrium,
    recommend_strategies,
)


class TestClassifySentiment(unittest.TestCase):
    def test_bullish_sentiment(self):
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 0.3, "pc_oi_ratio": 0.4,
                        "iv_skew": -0.1, "avg_implied_volatility": 0.25,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.BULLISH)
        self.assertGreater(confidence, 0.0)

    def test_bearish_sentiment(self):
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 2.0, "pc_oi_ratio": 1.8,
                        "iv_skew": 0.15, "avg_implied_volatility": 0.35,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.BEARISH)
        self.assertGreater(confidence, 0.0)

    def test_neutral_sentiment(self):
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 0.9, "pc_oi_ratio": 0.95,
                        "iv_skew": 0.01, "avg_implied_volatility": 0.25,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.NEUTRAL)

    def test_empty_data(self):
        sentiment, confidence = classify_sentiment({"expirations": []})
        self.assertEqual(sentiment, Sentiment.NEUTRAL)


class TestClassifyVolatility(unittest.TestCase):
    def test_high_volatility(self):
        data = {
            "expirations": [
                {"summary": {"avg_implied_volatility": 0.65}},
                {"summary": {"avg_implied_volatility": 0.70}},
            ]
        }
        vol, avg = classify_volatility(data)
        self.assertEqual(vol, Volatility.HIGH)
        self.assertGreater(avg, 0.5)

    def test_low_volatility(self):
        data = {
            "expirations": [
                {"summary": {"avg_implied_volatility": 0.15}},
                {"summary": {"avg_implied_volatility": 0.18}},
            ]
        }
        vol, avg = classify_volatility(data)
        self.assertEqual(vol, Volatility.LOW)
        self.assertLess(avg, 0.2)

    def test_normal_volatility(self):
        data = {
            "expirations": [
                {"summary": {"avg_implied_volatility": 0.30}},
            ]
        }
        vol, avg = classify_volatility(data)
        self.assertEqual(vol, Volatility.NORMAL)

    def test_empty_data(self):
        vol, avg = classify_volatility({"expirations": []})
        self.assertEqual(vol, Volatility.NORMAL)
        self.assertEqual(avg, 0.0)


class TestDarwinianQuality(unittest.TestCase):
    def test_stable_large_cap(self):
        """Stable sector, large cap, low beta = exceptional quality."""
        data = {
            "current_price": 150.0,
            "stock_info": {
                "sector": "Consumer Defensive",
                "beta": 0.6,
                "dividend_yield": 0.025,
                "market_cap": 500e9,
                "fifty_two_week_high": 180.0,
                "fifty_two_week_low": 120.0,
            },
        }
        quality, score, reasons = assess_darwinian_quality(data)
        self.assertIn(quality, (DarwinianQuality.EXCEPTIONAL, DarwinianQuality.GOOD))
        self.assertGreater(score, 0.0)

    def test_speculative_tech(self):
        """Fast-changing sector, no dividend, high beta = speculative."""
        data = {
            "current_price": 50.0,
            "stock_info": {
                "sector": "Technology",
                "beta": 2.5,
                "dividend_yield": 0.0,
                "market_cap": 500e6,
                "fifty_two_week_high": 150.0,
                "fifty_two_week_low": 30.0,
            },
        }
        quality, score, reasons = assess_darwinian_quality(data)
        self.assertIn(quality, (DarwinianQuality.POOR, DarwinianQuality.SPECULATIVE, DarwinianQuality.AVERAGE))

    def test_no_info(self):
        """No stock info should still return a reasonable default."""
        data = {"current_price": 100.0, "stock_info": {}}
        quality, score, reasons = assess_darwinian_quality(data)
        self.assertIn(quality, DarwinianQuality)


class TestPunctuatedEquilibrium(unittest.TestCase):
    def test_normal_conditions(self):
        """Normal conditions should not detect punctuation."""
        data = {
            "current_price": 150.0,
            "stock_info": {
                "fifty_two_week_high": 180.0,
                "fifty_two_week_low": 120.0,
            },
            "expirations": [
                {"summary": {"avg_implied_volatility": 0.25}},
            ],
        }
        result = detect_punctuated_equilibrium(data)
        self.assertFalse(result["is_punctuation"])

    def test_fear_punctuation(self):
        """Near 52-week low + high IV = fear punctuation."""
        data = {
            "current_price": 105.0,
            "stock_info": {
                "fifty_two_week_high": 200.0,
                "fifty_two_week_low": 100.0,
            },
            "expirations": [
                {"summary": {"avg_implied_volatility": 0.55}},
            ],
        }
        result = detect_punctuated_equilibrium(data)
        self.assertTrue(result["is_punctuation"])
        self.assertEqual(result["type"], "fear_punctuation")


class TestRecommendStrategies(unittest.TestCase):
    def test_recommend_returns_expected_keys(self):
        """Should return a dict with all expected Darwinian keys."""
        result = recommend_strategies({
            "ticker": "TEST",
            "current_price": 100.0,
            "fetch_time": "2026-01-01",
            "stock_info": {
                "sector": "Consumer Defensive",
                "beta": 0.6,
                "dividend_yield": 0.03,
                "market_cap": 200e9,
                "fifty_two_week_high": 120.0,
                "fifty_two_week_low": 80.0,
            },
            "expirations": [
                {
                    "expiration": "2026-01-15",
                    "days_to_expiry": 14,
                    "calls": [
                        {"strike": 95, "last_price": 6.0, "bid": 5.9, "ask": 6.1,
                         "volume": 1000, "open_interest": 5000, "implied_volatility": 0.25,
                         "in_the_money": True, "change": 0.1, "percent_change": 1.7},
                        {"strike": 100, "last_price": 3.0, "bid": 2.9, "ask": 3.1,
                         "volume": 2000, "open_interest": 8000, "implied_volatility": 0.28,
                         "in_the_money": False, "change": 0.1, "percent_change": 3.4},
                        {"strike": 105, "last_price": 1.0, "bid": 0.95, "ask": 1.05,
                         "volume": 500, "open_interest": 3000, "implied_volatility": 0.30,
                         "in_the_money": False, "change": -0.1, "percent_change": -9.1},
                    ],
                    "puts": [
                        {"strike": 95, "last_price": 1.0, "bid": 0.95, "ask": 1.05,
                         "volume": 500, "open_interest": 2000, "implied_volatility": 0.30,
                         "in_the_money": False, "change": 0.0, "percent_change": 0.0},
                        {"strike": 100, "last_price": 3.0, "bid": 2.9, "ask": 3.1,
                         "volume": 1500, "open_interest": 6000, "implied_volatility": 0.28,
                         "in_the_money": True, "change": 0.2, "percent_change": 7.1},
                        {"strike": 105, "last_price": 6.0, "bid": 5.9, "ask": 6.1,
                         "volume": 800, "open_interest": 4000, "implied_volatility": 0.26,
                         "in_the_money": True, "change": 0.3, "percent_change": 5.3},
                    ],
                    "summary": {
                        "atm_strike": 100.0,
                        "pc_volume_ratio": 0.73,
                        "pc_oi_ratio": 0.67,
                        "avg_implied_volatility": 0.28,
                        "iv_skew": -0.02,
                        "call_volume": 3500,
                        "put_volume": 2800,
                        "call_open_interest": 16000,
                        "put_open_interest": 12000,
                    },
                }
            ],
        })
        self.assertIn("recommendations", result)
        self.assertIn("darwinian_quality", result)
        self.assertIn("punctuated_equilibrium", result)
        self.assertIn("sentiment", result)
        self.assertIn("volatility", result)
        self.assertIn("philosophy", result)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_no_price_error(self):
        """No current price should return error."""
        result = recommend_strategies({"ticker": "TEST", "expirations": []})
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()