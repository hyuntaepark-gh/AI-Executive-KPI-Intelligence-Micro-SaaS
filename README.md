# 🚀 AI Executive KPI Intelligence Micro-SaaS

![FastAPI](https://img.shields.io/badge/FastAPI-Micro%20SaaS-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-KPI%20Warehouse-336791?logo=postgresql&logoColor=white)
![LLM Agent](https://img.shields.io/badge/LLM-Agent%20Intelligence-6A1B9A)
![Dynamic SQL](https://img.shields.io/badge/Dynamic-SQL%20Builder-0A66C2)
![Decision Engine](https://img.shields.io/badge/Decision-Intelligence-FF7043)
![Risk Scoring](https://img.shields.io/badge/Risk-Scoring%20Engine-2E7D32)
![Executive AI](https://img.shields.io/badge/Executive-AI%20Analytics-FF6F00)
![AI SaaS](https://img.shields.io/badge/AI-SaaS%20Architecture-232F3E)
![Driver Analysis](https://img.shields.io/badge/KPI-Driver%20Decomposition-00897B)
![CI](https://github.com/hyuntaepark-gh/AI-Executive-KPI-Intelligence-Micro-SaaS/actions/workflows/ci.yml/badge.svg)

> Built as a **Product-Grade AI Analytics Backend** demonstrating  
> Data Engineering, Backend Architecture, and Decision Intelligence design.

Ask questions like **"Why did performance drop?"** and receive automated driver analysis, risk signals, anomaly detection, and executive-ready AI insights.

---

# 🧨 What Makes This Different

Unlike traditional BI dashboards or simple LLM demos, this system:

- Combines deterministic data pipelines with LLM reasoning
- Executes real SQL queries instead of hallucinated outputs
- Implements fallback decision logic when AI parsing fails
- Produces structured analytics BEFORE generating narratives
- Simulates a production-grade AI analytics backend

👉 This is not a chatbot.  
👉 This is a **Decision Intelligence System**.

---

# 🧠 AI Executive Decision Intelligence Engine

This system simulates a modern AI analytics product that automatically:

- Detects KPI intent from natural language
- Generates dynamic SQL queries
- Performs driver decomposition
- Calculates risk signals
- Produces executive narratives
- Detects KPI anomalies
- Runs what-if simulations
- Supports async AI jobs

> ⚠️ Note:  
This system does NOT rely purely on LLMs.

- Core analytics are SQL-driven  
- KPI computations are deterministic  
- LLM is used only for interpretation and narrative generation  

This ensures reliability and prevents hallucinated business insights.

---

## ⚡ AI Insight Pipeline

```
User Question
→ Agent Intelligence
→ KPI Driver Analysis
→ Decision Engine
→ Executive Report
```

---

# 🏗️ Architecture

![System Architecture](docs/End-to-End%20System%20Architecture%20of%20the%20KPI%20Intelligence%20System.png)

---

## 🧱 System Design Highlights

- Microservice-style API architecture
- Separation of concerns (Agent / SQL / Decision Engine)
- Stateless API layer for scalability
- Pluggable LLM + rule-based hybrid system
- Production-style fallback handling

---

## Backend

- FastAPI
- Python
- Pydantic v2

## Data Layer

- PostgreSQL
- Dynamic SQL Builder

## AI / Decision Intelligence

- Agent Intelligence Engine
- Driver Decomposition Service
- Risk Scoring Engine
- Executive Narrative Generator
- KPI Anomaly Detection
- What-If Simulation Engine

## Infra

- Docker
- Docker Compose
- API Key Security

---

# 🖼️ Product Demo Screenshots

## 🚀 API Swagger Overview

![Swagger](docs/Micro-SaaS%20KPI%20Analytics%20API%20(FastAPI%20%2B%20Docker).png)

---

## 🧠 Executive Insight Endpoint

![Executive Insight](docs/Executive%20Insight%20Endpoint.png)

---

## 🐳 Docker Runtime

![Docker Running](docs/Docker%20ps%20screen.png)

---

# 🔐 Product API (v1)

All production endpoints live under:

`/v1/*`

Requires:

```
X-API-Key
```

Swagger → Use the **Authorize** button

---

# 🤖 AI Analytics Engine

## Primary Entry

```
POST /v1/agent/query
```

Natural language → Executive AI analysis.

Returns:

- driver_summary
- decision signals
- executive report

---

## Executive Narrative Only

```
POST /v1/ask-executive
```

Clean CFO-style output.

---

## 🧠 Debug Trace (Product-grade)

Shows:

- routing mode
- fallback decision
- agent execution trace

(No chain-of-thought exposed)

---

## 📈 Explain KPI Drivers (No LLM)

```
GET /v1/agent/explain
```

Rule-based KPI breakdown.

---

## 🚨 Auto Insight Detection

```
POST /v1/agent/insight
```

Detects KPI anomalies.

---

## 🔮 What-If Simulation

```
POST /v1/agent/simulate
```

Revenue ≈ Orders × AOV scenario testing.

---

# ⚡ Async AI Jobs (Senior DE Feature)

## Submit Async Query

```
POST /v1/agent/query-async
```

Returns:

```
job_id
```

---

## Poll Job Result

```
GET /v1/jobs/{job_id}
```

Simulates production AI background processing.

---

# 📊 Dashboard Endpoint (Frontend Ready)

```
GET /v1/dashboard
```

Provides:

- KPI tiles
- trend summary
- alerts
- risk signals

Designed for frontend MVP integration.

---

# 🎬 Demo Flow

## 1️⃣ Seed KPI Data

```
POST /v1/seed-demo
```


---

## 2️⃣ Ask Executive AI

POST /v1/ask-executive

Request Body:

{
  "question": "Why did performance drop?"
}

---

## 3️⃣ Detect KPI Risk

POST /v1/agent/insight

Request Body:

{}

---

## 4️⃣ Run What-If Simulation

POST /v1/agent/simulate

Request Body:

{
  "orders_delta_pct": 0.1
}

---

# 🧪 Real API Execution Proof (End-to-End AI Pipeline)

This section demonstrates **real execution of the AI analytics pipeline** using Swagger UI.

It validates:

- Full pipeline execution
- Agent routing behavior
- SQL-driven analytics
- Executive-level output generation

---

## 🔍 Scenario 1: Revenue Trend by Country

### 1️⃣ Debug Trace (Agent Routing)

![Debug Trend](docs/agent_debug_trend_country.png)

- Agent routing executed successfully
- Mode: `agent_llm`
- Pipeline initialized with correct intent

---

### 2️⃣ Agent Query (Structured Analytics Output)

![Query Trend](docs/agent_query_trend_country.png)

- Generated structured plan:
  - intent: `trend`
  - metric: `revenue`
  - breakdown: `country`
- Returned time-series KPI data

---

### 3️⃣ Executive Report (Final AI Output)

![Executive Trend](docs/executive_report_trend_country.png)

- CFO-style narrative generated automatically
- Key insights:
  - US highest revenue contributor
  - Germany/Canada variability
  - Korea/Japan stable trends
- Actionable recommendations included

---

## 🔎 Scenario 2: Revenue Drop Analysis

### 1️⃣ Debug Trace (Fallback + Decision Logic)

![Debug Drop](docs/agent_debug_revenue_drop.png)

- Initial agent parsing failed
- Fallback triggered: `multi_metric_fallback`
- Decision engine handled ambiguity correctly

---

### 2️⃣ Agent Query (Comparative KPI Analysis)

![Query Drop](docs/agent_query_revenue_drop.png)

- Intent: `explain`
- Comparison: `previous_period`
- Output:
  - revenue decreased from 83,531 → 70,878

---

### 3️⃣ Executive Report (Final Business Insight)

![Executive Drop](docs/executive_report_revenue_drop.png)

- AI-generated executive summary:
  - Significant revenue decline detected
  - No detailed driver breakdown available
- Recommended next steps:
  - Segment-level analysis
  - Pricing / marketing investigation

---

## 🧠 What This Proves

This is **not a toy LLM demo**.

It demonstrates a **production-style AI analytics system**:

✔ Natural Language → KPI Intent Detection  
✔ Dynamic Query Planning  
✔ SQL-based Data Retrieval  
✔ Driver / Trend Analysis  
✔ Decision Engine Fallback Logic  
✔ Executive Narrative Generation  

---

## 🏆 Key Technical Validation

- Multi-stage AI pipeline execution
- Deterministic + LLM hybrid system
- Failure recovery (fallback routing)
- Real API responses (not mocked)
- Production-ready architecture

---

# ⚡ Quick Start

git clone https://github.com/hyuntaepark-gh/AI-Executive-KPI-Intelligence-Micro-SaaS.git  
cd AI-Executive-KPI-Intelligence-Micro-SaaS  

docker compose up --build  

Open:  
http://localhost:8000/docs  

1. Click "Authorize"  
2. Enter API Key: dev-secret-key  
3. Try /v1/ask-executive  

---

# 🐳 Run with Docker

```
docker compose up --build
```

Swagger:

```
http://localhost:8000/docs
```

---

# 🎯 Why This Project Matters

Modern analytics platforms are evolving into **Decision Intelligence Systems**.

This project demonstrates:

- AI Agent-driven analytics
- Executive-level KPI reasoning
- Product-grade FastAPI architecture
- Async AI job processing
- Frontend-ready API design
- Micro-SaaS backend system

---

# 💼 Example Use Cases

- Executive KPI monitoring  
- Revenue anomaly detection  
- Business performance diagnosis  
- Decision support systems  

---

# 📊 Performance

- API latency: ~400–600ms  
- Query execution: <200ms  
- Async job support for scalability  

---

# 🧩 Designed For

- AI Backend Engineering
- Data Engineering (API-first analytics)
- Decision Intelligence Systems
- Micro-SaaS Architecture

---

# 🧠 Positioning

```
BI Dashboard → AI Analytics Engine → Decision Intelligence SaaS
```

---

# 🔎 API Examples

### Example 1) Executive KPI Explanation

**Request**

```
curl -X POST "http://localhost:8000/v1/ask-executive" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test" \
  -d '{
    "question": "Why did revenue drop last month?"
  }'
```

**Response**

```
{
  "answer": "Revenue declined primarily due to fewer orders, while average order value remained relatively stable.",
  "driver_summary": {
    "primary_driver": "orders"
  }
}
```
### Example 2) What-If Simulation

**Request**

```
curl -X POST "http://localhost:8000/v1/agent/simulate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test" \
  -d '{
    "orders_delta_pct": 0.10
  }'
```

**Response**

```
{
  "baseline": {
    "orders": 12400,
    "aov": 58.2,
    "revenue": 721680
  },
  "scenario": {
    "orders": 13640,
    "aov": 58.2,
    "revenue": 794848
  },
  "delta": {
    "orders": 1240,
    "revenue": 73168
  }
}
```


---

## 🗺️ Data Model (ERD)

![ERD](docs/erd.png)

### Core Tables

**mart_kpi_monthly**
- month (PK)
- revenue
- orders
- customers
- aov

**fact_orders**
- order_id (PK)
- order_date
- customer_id
- product_id
- revenue

**dim_customer**
- customer_id (PK)
- country
- segment

**dim_product**
- product_id (PK)
- category
- price

---

# 📂 Project Structure

```
AI-Executive-KPI-Intelligence-Micro-SaaS/
├── .github/workflows/   # CI/CD workflows
├── api/                 # FastAPI app and backend logic
├── db/                  # Database scripts and initialization files
├── docs/                # ERD, architecture diagrams, and project docs
├── tests/               # Test cases
├── .env.example         # Environment variables template (API keys, DB config)
├── .gitignore           # Ignore secrets, cache files, and local environments
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Multi-container local setup
└── README.md
```
