# Sentiment Monitor 散戶情緒監控

零售投資者情緒監控系統，追蹤 Reddit 和 Twitter 上的股票討論熱度與情緒。

Retail investor sentiment monitoring system that tracks stock discussion heat and sentiment on Reddit and Twitter.

## Features 功能

- **Reddit Sentiment Analysis** - 從 Reddit 熱門板塊獲取情緒數據
- **Twitter Sentiment** - 追蹤 Twitter/X 熱門話題
- **Risk Assessment** - 風險等級評估 (高/中/低)
- **Market Direction** - 市場風向分析
- **Index Tracking** - 追蹤 S&P 500、NASDAQ、Dow Jones 三大指數
- **Holdings Analysis** - 自動分析持股情緒

## Installation 安裝

```bash
# Clone the repository
git clone https://github.com/arbiger/sentiment-monitor.git
cd sentiment-monitor

# Install dependencies
pip install -r requirements.txt
```

## Dependencies 依賴

```
vaderSentiment>=3.3.2
textblob>=0.17.1
praw>=7.7.0
requests>=2.31.0
```

```bash
# Or install via pip
pip install vaderSentiment textblob praw requests
```

## Usage 使用方法

```bash
# Analyze market indices (S&P 500, NASDAQ, Dow Jones)
python3 scripts/sentiment.py indices

# Analyze your holdings (reads from holdings.md)
python3 scripts/sentiment.py holdings

# Analyze specific stock
python3 scripts/sentiment.py NVDA
python3 sentiment.py TSLA
python3 sentiment.py HIMS

# Trending topics
python3 scripts/sentiment.py trending

# Full report
python3 scripts/sentiment.py full
```

## Output Examples 輸出範例

### Index Analysis 指數分析
```
## 📊 散戶情緒報告 - 2026-03-15

### 🏛️ 三大指數情緒
| 指數 | 名稱 | 情緒 |
|------|------|------|
| SPY | S&P 500 | 😐 50% |
| QQQ | NASDAQ 100 | 😐 53% |
| DIA | Dow Jones | 😐 48% |
```

### Stock Analysis 股票分析
```
### 📈 NVDA 情緒分析

| 指標 | 數值 |
|------|------|
| Reddit 情緒 | 😐 51% (中性觀望) |
| 風險等級 | 🟢 低 |
```

## Sentiment Methodology 情緒分析方法

### Level 1: Keyword Matching 關鍵詞匹配
- Bullish: buy, long, bullish, call, to the moon...
- Bearish: sell, short, bearish, puts, dump...

### Level 2: VADER Sentiment Analysis
- Uses VADER (Valence Aware Dictionary and sEntiment Reasoner)
- Compound score: -1 (negative) to +1 (positive)

### Level 3: Risk Assessment 風險評估
| Level 等級 | Keywords 關鍵詞 |
|-----------|----------------|
| 🔴 High 高風險 | YOLO, all in, short squeeze, gamma ramp |
| 🟡 Medium 中風險 | options, calls, puts, squeeze |
| 🟢 Low 低風險 | DD, fundamentals, valuation, dividend |

## Risk Warning 風險聲明

此分析僅供參考，不構成投資建議。散戶情緒往往是反向指標，請謹慎使用。

This analysis is for reference only and does not constitute investment advice. Retail sentiment is often a contrarian indicator - use with caution.

## License 授權

MIT License

## Author

- GitHub: [@arbiger](https://github.com/arbiger)
