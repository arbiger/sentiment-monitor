---
name: sentiment-monitor
description: 散戶情緒監控 - 從 Reddit 和 Twitter 收集股票討論情緒，分析市場風向、風險等級和熱門話題。輸入：持股清單或指定股票。輸出：情緒分數、風險等級、市場風向報告。
---

# Sentiment Monitor

散戶情緒監控系統，追蹤 Reddit 和 Twitter 上的股票討論熱度與情緒。

## 定位

當用戶詢問以下問題時觸發：
- 「現在市場情緒怎麼樣？」
- 「[股票] 討論熱度怎麼樣？」
- 「有什麼熱門股票嗎？」
- 「分析我的持股情緒」
- 「市場風向」

## 數據來源

| 來源 | 用途 |
|------|------|
| Reddit | 專業討論區 (r/investing, r/stocks, r/WSB 等) |
| Twitter/X | 熱門話題與即時討論 |
| Polymarket | 市場預期 (輔助) |

### 監控的 Subreddits

| 類別 | Subreddits |
|------|------------|
| 風險/ Meme | r/WallStreetBets, r/amcstock, r/GME, r/pennystocks |
| 市場資訊 | r/stocks, r/StockMarket, r/StockMarketNews |
| 價值投資 | r/investing, r/ValueInvesting, r/SecurityAnalysis |
| 股息投資 | r/dividendinvesting |

## 執行流程

```
Step 1: 確認輸入
    │
    ├─ 有持股清單 → 讀取 holdings.md
    │
    └─ 用戶指定股票 → 使用指定股票

Step 2: 數據收集
    │
    ├─ Reddit 搜尋 (PRAW 或 web fetch)
    ├─ Twitter 搜尋 (.twint 或 API)
    └─ 情緒分析

Step 3: 情緒分析
    │
    ├─ Level 1: 關鍵詞匹配
    ├─ Level 2: VADER/TextBlob 語意分析
    └─ Level 3: 進階分析 (可選)

Step 4: 風險評估
    │
    ├─ 高風險關鍵詞檢測
    ├─ Meme 股識別
    └─ 風險等級輸出

Step 5: 輸出報告
    │
    ├─ 持股情緒
    ├─ 熱門話題
    └─ 市場風向
```

## 情緒分析方法

### Level 1: 關鍵詞匹配

| 正面關鍵詞 | 負面關鍵詞 |
|------------|------------|
| buy, long, bullish | sell, short, bearish |
| to the moon, diamond hands | crash, dump, rip |
| call, leap | put, gamma squeeze |

### Level 2: 語意分析

使用 VADER (Valence Aware Dictionary and sEntiment Reasoner) 計算情緒分數：
- **Compound Score**: -1 (最負面) 到 +1 (最正面)
- 權重參考 upvotes 數量

### Level 3: 進階分析 (可選)

| 分析 | 內容 |
|------|------|
| DD 質量 | 是否有基本面數據支撐 |
| 時間趨勢 | 情緒是否在惡化/好轉 |
| 機構信號 | 是否提及機構買賣 |

## 風險評估

### 風險關鍵詞

| 等級 | 關鍵詞 |
|------|--------|
| 🔴 高風險 | YOLO, all in, to the moon, short squeeze, gamma ramp, 100x |
| 🟡 中風險 | options, calls, puts, leap, squeeze |
| 🟢 低風險 | DD, fundamentals, valuation, dividend |

### 風險等級標準

| 等級 | 標準 |
|------|------|
| 🔴 高風險 | 高風險關鍵詞 >30% + Meme 股上榜 |
| 🟡 中風險 | 中風險關鍵詞 >20% |
| 🟢 低風險 | 基本面關鍵詞 >50% |

## 輸出範例

### 持股情緒報告

```markdown
## 📊 散戶情緒報告 - [日期]

### 你的持股情緒
| 股票 | Reddit情緒 | Twitter情緒 | 綜合 | 風險 |
|------|------------|------------|------|------|
| NVDA | 🐂 75% | 🐂 80% | 🐂 77% | 🟢 低 |
| HIMS | 🐻 35% | 😐 50% | 😐 42% | 🟡 中 |
| GOOG | 🐂 60% | 🐂 65% | 🐂 62% | 🟢 低 |

### 市場風向
- **熱門板塊**: AI/科技 (42%), 醫療 (18%), 能源 (15%)
- **整體情緒**: 🐂 62% Bullish
- **風險指數**: 🟡 中等

### 警示
⚠️ GME 討論量激增 300%，注意逼空風險
⚠️ PLTR 出現在 WSB 熱門討論中
```

### 熱門話題報告

```markdown
## 🔥 熱門話題

### Reddit 熱門
1. #GME - 240 comments, 🐂 78%
2. #NVDA - 180 comments, 🐂 82%
3. #PLTR - 95 comments, 🐂 65%

### Twitter 趨勢
1. #AIStocks - 2.5K mentions
2. #MemeStocks - 1.8K mentions

### Polymarket 輔助
- 市場情緒偏空 (67% 預期 <$6000)
```

## 使用方式

```bash
# 分析持股情緒
python3 scripts/sentiment.py holdings

# 分析特定股票
python3 scripts/sentiment.py NVDA

# 熱門話題
python3 scripts/sentiment.py trending

# 完整報告
python3 scripts/sentiment.py full
```

## Dependencies

```bash
# Python dependencies
pip install praw vaderSentiment textblob requests

# 可選
# pip install tweepy (Twitter API)
# pip install snscrape (Twitter scraping)
```

## 限制與注意事項

1. **數據延遲**: Reddit/Twitter 是落後指標
2. **雜訊**: 很多是情緒發洩，非投資建議
3. **語言**: 主要針對英文內容
4. **API 限制**: 可能需要設定 API keys

## 風險聲明

此分析僅供參考，不構成投資建議。散戶情緒往往是反向指標，請謹慎使用。
