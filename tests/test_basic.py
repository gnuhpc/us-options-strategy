#!/usr/bin/env python3
"""Basic tests for the options strategy scripts."""

import json
import sys
import os
import unittest

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.strategies import (
    classify_sentiment,
    classify_volatility,
    Sentiment,
    Volatility,
    recommend_strategies,
)


class TestClassifySentiment(unittest.TestCase):
    def test_bullish_sentiment(self):
        """Low PC ratio should indicate bullish sentiment."""
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 0.3,
                        "pc_oi_ratio": 0.4,
                        "iv_skew": -0.1,
                        "avg_implied_volatility": 0.25,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.BULLISH)
        self.assertGreater(confidence, 0.0)

    def test_bearish_sentiment(self):
        """High PC ratio should indicate bearish sentiment."""
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 2.0,
                        "pc_oi_ratio": 1.8,
                        "iv_skew": 0.15,
                        "avg_implied_volatility": 0.35,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.BEARISH)
        self.assertGreater(confidence, 0.0)

    def test_neutral_sentiment(self):
        """Balanced ratios should indicate neutral sentiment."""
        data = {
            "expirations": [
                {
                    "summary": {
                        "pc_volume_ratio": 0.9,
                        "pc_oi_ratio": 0.95,
                        "iv_skew": 0.01,
                        "avg_implied_volatility": 0.25,
                    }
                }
            ]
        }
        sentiment, confidence = classify_sentiment(data)
        self.assertEqual(sentiment, Sentiment.NEUTRAL)

    def test_empty_data(self):
        """Empty data should return neutral."""
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


class TestRecommendStrategies(unittest.TestCase):
    def test_recommend_returns_list(self):
        """Should return a dict with recommendations."""
        result = recommend_strategies({
            "ticker": "TEST",
            "current_price": 100.0,
            "fetch_time": "2026-01-01",
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
        self.assertIn("sentiment", result)
        self.assertIn("volatility", result)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_no_data_error(self):
        """No current price should return error."""
        result = recommend_strategies({"ticker": "TEST", "expirations": []})
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()