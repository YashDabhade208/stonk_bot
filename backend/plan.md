# Stock Analytics App – Backend Plan (Node.js) – Phase 1

## Objective

Build a backend service that provides structured stock data for a ticker:

Features returned to frontend:

* Summary
* Price Chart Data
* Profit & Loss
* Quarterly Results
* Peer Companies
* Basic Analysis Metrics

Phase 1 = **Data backend + APIs**

Phase 2 = **AI risk analysis chatbot**

---

# 1. High Level Architecture

```
Frontend (React / Next.js)
        |
        v
Backend API (Node.js / NestJS or Express)
        |
        +----- Stock Data Service
        |
        +----- Financial Data Service
        |
        +----- Analytics Engine
        |
        +----- Cache (Redis)
        |
        +----- Database (PostgreSQL)
        |
        +----- External APIs
              |-- Financial Modeling Prep
              |-- Yahoo Finance
              |-- Alpha Vantage
```

---

# 2. Tech Stack

### Backend

Recommended:

```
Node.js
Express.js
```

Better (for scale):

```
NestJS
```

---

### Database

```
PostgreSQL
```

Reason:

* structured financial data
* strong relational queries
* good analytics support

---

### Cache

```
Redis
```

Used for:

* API caching
* rate limiting
* preventing provider abuse

---

### HTTP Client

```
Axios
```

or

```
node-fetch
```

---

### ORM

Choose one:

```
Prisma (Recommended)
```

or

```
Sequelize
```

---

# 3. External Data Providers

Pick **1 main + 1 fallback**

### Option 1 (Best)

Financial Modeling Prep

```
https://financialmodelingprep.com
```

Good endpoints:

```
/profile
/income-statement
/key-metrics
/stock_peers
/historical-price-full
```

---

### Option 2

Yahoo Finance

Use npm package:

```
yahoo-finance2
```

---

# 4. Backend Folder Structure

```
backend
│
├── src
│
│   ├── controllers
│   │      stockController.js
│
│   ├── services
│   │      stockService.js
│   │      financialService.js
│   │      analyticsService.js
│
│   ├── providers
│   │      fmpProvider.js
│   │      yahooProvider.js
│
│   ├── routes
│   │      stockRoutes.js
│
│   ├── models
│   │      stockModel.js
│   │      financialModel.js
│
│   ├── db
│   │      prismaClient.js
│
│   ├── cache
│   │      redisClient.js
│
│   ├── utils
│   │      calculations.js
│
│   └── app.js
│
├── prisma
│      schema.prisma
│
├── package.json
└── server.js
```

---

# 5. API Endpoints

## Stock Summary

```
GET /api/stock/:ticker/summary
```

Response:

```
{
  ticker: "AAPL",
  name: "Apple Inc",
  sector: "Technology",
  marketCap: 2800000000000,
  peRatio: 32,
  dividendYield: 0.6,
  week52High: 198,
  week52Low: 124
}
```

---

## Price Chart

```
GET /api/stock/:ticker/chart
```

Query Params:

```
range=1y
interval=1d
```

Response:

```
{
  dates: [],
  prices: [],
  volumes: []
}
```

---

## Profit & Loss

```
GET /api/stock/:ticker/financials
```

Response:

```
{
  revenue: [],
  netIncome: [],
  eps: [],
  grossMargin: []
}
```

---

## Quarterly Results

```
GET /api/stock/:ticker/quarters
```

Response:

```
[
  {
    quarter: "Q1 2024",
    revenue: 12000000000,
    profit: 2400000000
  }
]
```

---

## Peer Companies

```
GET /api/stock/:ticker/peers
```

Response:

```
[
  "MSFT",
  "GOOGL",
  "AMZN"
]
```

---

## Basic Analysis

```
GET /api/stock/:ticker/analysis
```

Response:

```
{
  revenueGrowth: "12%",
  earningsGrowth: "18%",
  marginTrend: "improving",
  valuation: "slightly_overvalued"
}
```

---

# 6. Database Schema (Prisma)

## stocks

```
model Stock {
  ticker        String   @id
  name          String
  sector        String
  industry      String
  marketCap     Float
  updatedAt     DateTime
}
```

---

## stock_prices

```
model StockPrice {
  id       Int @id @default(autoincrement())
  ticker   String
  date     DateTime
  open     Float
  high     Float
  low      Float
  close    Float
  volume   Float
}
```

---

## financials

```
model Financial {
  id         Int @id @default(autoincrement())
  ticker     String
  year       Int
  revenue    Float
  netIncome  Float
  eps        Float
  grossProfit Float
}
```

---

## quarterly_results

```
model Quarterly {
  id        Int @id @default(autoincrement())
  ticker    String
  quarter   String
  revenue   Float
  profit    Float
  eps       Float
}
```

---

## peers

```
model Peer {
  id        Int @id @default(autoincrement())
  ticker    String
  peer      String
}
```

---

# 7. Data Flow

When user requests stock data:

```
1 User sends ticker
2 Backend checks Redis cache
3 If cache miss
4 Fetch from provider API
5 Normalize response
6 Save in PostgreSQL
7 Cache result
8 Return response
```

---

# 8. Caching Strategy

Use Redis keys:

```
stock:summary:{ticker}
stock:chart:{ticker}
stock:financials:{ticker}
stock:analysis:{ticker}
```

TTL example:

```
summary -> 24h
financials -> 24h
charts -> 5m
analysis -> 1h
```

---

# 9. Analytics Engine

Calculate metrics in service layer.

Example:

Revenue growth

```
(currentYearRevenue - previousYearRevenue) / previousYearRevenue
```

Profit margin

```
netIncome / revenue
```

Other metrics:

```
PE ratio
EV / EBITDA
ROE
ROA
Debt to Equity
```

---

# 10. Rate Limiting

External APIs have limits.

Add:

```
Retry logic
Provider fallback
Queue system
```

Libraries:

```
axios-retry
p-limit
bottleneck
```

---

# 11. Deployment

Containerize with Docker.

Stack:

```
Node.js
PostgreSQL
Redis
Docker
```

Deployment options:

```
Railway
Render
AWS ECS
Fly.io
```

---

# 12. Phase 2 (AI Layer)

Add endpoint:

```
POST /api/stock/:ticker/ai-analysis
```

AI features:

* risk score
* future outlook
* valuation analysis
* earnings trend explanation
* peer comparison

Possible stack:

```
LLM
Vector DB
Financial embeddings
```

---

# 13. Future Features

```
Portfolio tracking
Watchlists
Price alerts
Institutional ownership
Insider trades
News sentiment
Earnings transcript AI
```

---

# 14. MVP Timeline

Week 1

```
API provider integration
summary endpoint
chart endpoint
```

Week 2

```
financials
quarterly results
peers
```

Week 3

```
analytics engine
redis caching
```

Week 4

```
deployment
production APIs
```

---

# Final MVP Output

User input:

```
AAPL
```

Backend returns:

```
summary
chart
financials
quarters
peers
analysis
```

Frontend renders dashboard.
