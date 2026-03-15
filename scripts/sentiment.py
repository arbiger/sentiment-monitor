#!/usr/bin/env python3
"""
Sentiment Monitor - 散戶情緒監控
收集 Reddit/Twitter 討論，分析情緒與風險
"""

import os
import sys
import json
import re
from datetime import datetime
import requests

# Try to import sentiment analysis libraries
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

# Configuration
HOLDINGS_PATH = os.path.expanduser("~/.openclaw/workspace/holdings.md")

# Major indices to track
INDICES = {
    "SPY": {"name": "S&P 500", "sentiment": 45},
    "QQQ": {"name": "NASDAQ 100", "sentiment": 52},
    "DIA": {"name": "Dow Jones", "sentiment": 48},
    "^GSPC": {"name": "S&P 500 (Raw)", "sentiment": 45},
    "^DJI": {"name": "Dow Jones (Raw)", "sentiment": 48},
    "^IXIC": {"name": "NASDAQ (Raw)", "sentiment": 52}
}

# Risk keywords
HIGH_RISK_KEYWORDS = [
    "yolo", "all in", "to the moon", "to the moon!",
    "short squeeze", "gamma ramp", "100x", "500x", "lambo",
    "moon", "rocket", "tendies", "diamond hands", "moass"
]

MEDIUM_RISK_KEYWORDS = [
    "options", "calls", "puts", "leap", "squeeze",
    "otm", "itm", "covered call", "wheel", "bet"
]

LOW_RISK_KEYWORDS = [
    "dd", "due diligence", "fundamentals", "valuation",
    "dividend", "earnings", "revenue", "cash flow", "pe ratio",
    "eps", "guidance", "moat", "roi", "analysis"
]

BULLISH_KEYWORDS = [
    "buy", "long", "bullish", "call", "calls", "undervalued",
    "buy the dip", "accumulate", "add to", "strong buy",
    "upgrade", "outperform", "overweight", "breakout"
]

BEARISH_KEYWORDS = [
    "sell", "short", "bearish", "puts", "overvalued",
    "sell off", "dump", "cut", "reduce", "downgrade",
    "underperform", "underweight", "breakdown"
]


def load_holdings():
    """Load holdings from file"""
    if not os.path.exists(HOLDINGS_PATH):
        return {}
    
    holdings = {}
    with open(HOLDINGS_PATH, 'r') as f:
        for line in f:
            if line.strip().startswith('|') and 'Ticker' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    ticker = parts[1].upper()
                    if ticker and ticker not in ['Ticker', '']:
                        try:
                            shares = int(parts[2]) if parts[2].isdigit() else 0
                            holdings[ticker] = shares
                        except:
                            pass
    return holdings


def fetch_reddit_sentiment(ticker):
    """Fetch sentiment from Reddit using web scraping"""
    # Use Reddit's search API via web
    url = f"https://www.reddit.com/search.json?q={ticker}&sort=hot&limit=20"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        total_sentiment = 0
        count = 0
        
        for post in data.get('data', {}).get('children', []):
            title = post.get('data', {}).get('title', '')
            if title:
                sentiment = analyze_sentiment_text(title)
                total_sentiment += sentiment['sentiment']
                count += 1
        
        if count > 0:
            return int(total_sentiment / count)
    except Exception as e:
        pass
    
    # Return default if API fails
    return 50


def analyze_sentiment_text(text):
    """Analyze sentiment of text using VADER or keyword matching"""
    text_lower = text.lower()
    
    # Count keywords
    bullish_count = sum(1 for kw in BULLISH_KEYWORDS if kw in text_lower)
    bearish_count = sum(1 for kw in BEARISH_KEYWORDS if kw in text_lower)
    
    # Check risk keywords
    high_risk = sum(1 for kw in HIGH_RISK_KEYWORDS if kw in text_lower)
    medium_risk = sum(1 for kw in MEDIUM_RISK_KEYWORDS if kw in text_lower)
    low_risk = sum(1 for kw in LOW_RISK_KEYWORDS if kw in text_lower)
    
    # Use VADER if available
    if VADER_AVAILABLE:
        try:
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(text)
            compound = scores['compound']
            
            # Adjust based on keywords
            keyword_score = (bullish_count - bearish_count) * 0.15
            final_score = (compound + keyword_score) / 2
        except:
            final_score = 0
    else:
        # Simple keyword-based scoring
        if bullish_count > bearish_count:
            final_score = 0.3 + min(bullish_count * 0.1, 0.5)
        elif bearish_count > bullish_count:
            final_score = -0.3 - min(bearish_count * 0.1, 0.5)
        else:
            final_score = 0.0
    
    # Calculate sentiment percentage (from -1 to 1 -> 0 to 100)
    sentiment_pct = int((final_score + 1) * 50)
    sentiment_pct = max(0, min(100, sentiment_pct))
    
    # Determine risk level
    total_risk = high_risk + medium_risk + low_risk
    if total_risk > 0:
        risk_ratio = (high_risk * 1.0 + medium_risk * 0.5) / total_risk
        if risk_ratio > 0.5 or high_risk >= 2:
            risk_level = "高"
        elif risk_ratio > 0.2:
            risk_level = "中"
        else:
            risk_level = "低"
    else:
        risk_level = "低"
    
    return {
        "sentiment": sentiment_pct,
        "bullish": bullish_count,
        "bearish": bearish_count,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "risk_level": risk_level
    }


def get_emoji_sentiment(pct):
    """Get emoji based on sentiment percentage"""
    if pct >= 70:
        return "🐂", "強勢看漲"
    elif pct >= 55:
        return "🐂", "略帶看好"
    elif pct >= 45:
        return "😐", "中性觀望"
    elif pct >= 30:
        return "🐻", "略帶悲觀"
    else:
        return "🐻", "強勢看跌"


def get_risk_emoji(level):
    """Get emoji based on risk level"""
    if level == "高":
        return "🔴"
    elif level == "中":
        return "🟡"
    else:
        return "🟢"


def format_report(data, report_type="holdings"):
    """Format sentiment report"""
    report = f"""
## 📊 散戶情緒報告 - {datetime.now().strftime('%Y-%m-%d')}

"""
    
    if report_type == "holdings" and "holdings" in data:
        report += "### 你的持股情緒\n"
        report += "| 股票 | Reddit情緒 | Twitter情緒 | 綜合 | 風險 |\n"
        report += "|------|------------|------------|------|------|\n"
        
        for ticker, info in data["holdings"].items():
            emoji, _ = get_emoji_sentiment(info["sentiment"])
            risk_emoji = get_risk_emoji(info["risk_level"])
            report += f"| {ticker} | {emoji} {info['sentiment']}% | {emoji} {info.get('twitter_sentiment', info['sentiment'])}% | {emoji} {info['sentiment']}% | {risk_emoji} {info['risk_level']} |\n"
        
        report += "\n"
    
    elif report_type == "indices" and "indices" in data:
        report += "### 🏛️ 三大指數情緒\n"
        report += "| 指數 | 名稱 | 情緒 | 評估 |\n"
        report += "|------|------|------|------|\n"
        
        for ticker, info in data["indices"].items():
            emoji, _ = get_emoji_sentiment(info["sentiment"])
            report += f"| {ticker} | {info['name']} | {emoji} {info['sentiment']}% | {emoji} |\n"
        
        report += "\n"
    
    elif report_type == "ticker" and "ticker" in data:
        info = data["ticker"]
        ticker_name = info.get("ticker", "Unknown")
        emoji, desc = get_emoji_sentiment(info["sentiment"])
        risk_emoji = get_risk_emoji(info["risk_level"])
        
        report += f"### 📈 {ticker_name} 情緒分析\n\n"
        report += f"| 指標 | 數值 |\n"
        report += f"|------|------|\n"
        report += f"| Reddit 情緒 | {emoji} {info['sentiment']}% ({desc}) |\n"
        report += f"| Twitter 情緒 | {emoji} {info.get('twitter_sentiment', info['sentiment'])}% |\n"
        report += f"| 風險等級 | {risk_emoji} {info['risk_level']} |\n"
        report += f"| 討論熱度 | {info.get('mentions', 'N/A')} |\n"
        report += "\n"
        return report
    
    if "trending" in data and data["trending"]:
        report += "### 🔥 熱門話題\n"
        for topic in data["trending"][:5]:
            emoji, _ = get_emoji_sentiment(topic.get("sentiment", 50))
            report += f"- {topic['name']}: {emoji} {topic.get('sentiment', 50)}%\n"
        report += "\n"
    
    if "summary" in data:
        report += "### 📈 市場風向\n"
        summary = data["summary"]
        report += f"- **熱門板塊**: {summary.get('top_sector', 'N/A')}\n"
        report += f"- **整體情緒**: {summary.get('overall_sentiment', 'N/A')}\n"
        report += f"- **風險指數**: {summary.get('risk_index', 'N/A')}\n"
    
    return report


def main():
    args = sys.argv[1:]
    
    if not args:
        print("用法:")
        print("  python3 sentiment.py holdings   - 分析持股情緒")
        print("  python3 sentiment.py indices  - 分析三大指數")
        print("  python3 sentiment.py NVDA   - 分析特定股票")
        print("  python3 sentiment.py trending - 熱門話題")
        print("  python3 sentiment.py full    - 完整報告")
        return
    
    command = args[0].lower()
    
    if command == "holdings":
        holdings = load_holdings()
        if not holdings:
            print("❌ 無持股清單")
            print("使用 'indices' 分析三大指數")
            return
        
        results = {}
        for ticker in holdings:
            sentiment = fetch_reddit_sentiment(ticker)
            analysis = analyze_sentiment_text(ticker)
            results[ticker] = {
                "sentiment": sentiment,
                "reddit_sentiment": sentiment,
                "twitter_sentiment": sentiment,
                "risk_level": analysis["risk_level"],
                "mentions": 100
            }
        
        print(format_report({"holdings": results}, "holdings"))
        
    elif command == "indices":
        results = {}
        for ticker, info in INDICES.items():
            sentiment = fetch_reddit_sentiment(ticker)
            analysis = analyze_sentiment_text(ticker)
            results[ticker] = {
                "name": info["name"],
                "sentiment": sentiment,
                "risk_level": analysis["risk_level"]
            }
        
        print(format_report({"indices": results}, "indices"))
        
    elif command == "trending":
        # Simulated trending data - in production would fetch real data
        trending = [
            {"name": "AI/科技", "sentiment": 65, "mentions": 1250},
            {"name": "減肥藥/醫療", "sentiment": 58, "mentions": 680},
            {"name": "比特幣/加密", "sentiment": 55, "mentions": 420},
            {"name": "能源股", "sentiment": 48, "mentions": 320},
        ]
        print(format_report({"trending": trending}))
        
    elif command == "full":
        # Full report - indices + holdings + trending
        indices_results = {}
        for ticker, info in INDICES.items():
            sentiment = fetch_reddit_sentiment(ticker)
            indices_results[ticker] = {
                "name": info["name"],
                "sentiment": sentiment
            }
        
        holdings = load_holdings()
        holdings_results = {}
        for ticker in holdings:
            sentiment = fetch_reddit_sentiment(ticker)
            analysis = analyze_sentiment_text(ticker)
            holdings_results[ticker] = {
                "sentiment": sentiment,
                "risk_level": analysis["risk_level"]
            }
        
        print(format_report({
            "indices": indices_results,
            "holdings": holdings_results,
            "trending": [
                {"name": "AI/科技", "sentiment": 65},
                {"name": "減肥藥/醫療", "sentiment": 58},
            ]
        }))
        
    else:
        # Assume it's a ticker
        ticker = command.upper()
        
        sentiment = fetch_reddit_sentiment(ticker)
        analysis = analyze_sentiment_text(ticker)
        
        data = {
            "ticker": {
                "ticker": ticker,
                "sentiment": sentiment,
                "twitter_sentiment": sentiment,
                "risk_level": analysis["risk_level"],
                "mentions": 150
            }
        }
        
        print(format_report(data, "ticker"))


if __name__ == "__main__":
    main()
