<div align="center">

# ⚡ AIManage

**AI Cost Management Middleware · Unified Proxy · Accurate Billing · Cost Insight · Budget Alerts**

*Make every LLM call traceable, analyzable, and controllable*

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](./docker-compose.yml)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Django](https://img.shields.io/badge/Django-5-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com)
[![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

[中文文档](./README.zh-CN.md) · [Architecture](./ARCHITECTURE.md)

</div>

---

## 📖 Table of Contents

- [What is this?](#-what-is-this)
- [Key Highlights](#-key-highlights)
- [Why This Project is Useful](#-why-this-project-is-useful)
- [UI Preview](#-ui-preview)
- [Usage Guide](#-usage-guide)
- [Tech Stack Overview](#-tech-stack-overview)
- [Architecture](#-architecture)
- [Core File Structure](#-core-file-structure)
- [Quick Start](#-quick-start)
- [Requirements](#-requirements)
- [FAQ](#-faq)
- [Security & Production Notes](#-security--production-notes)
- [License](#-license)

---

## 🔍 What is this?

AIManage is a **cost management middleware** for **AI Agent / LLM call scenarios**.

Its goal is not to replace orchestration platforms, but to centralize **LLM spend, call tracing, and budget control** — the three things teams struggle with most.

Once users or agents point the API endpoint to your gateway, you get:

- **Token-level and cost tracking** for every LLM call
- Cost dashboards by **Agent / Model / Time**
- **Budget alerts** with automatic notifications when thresholds are exceeded
- Team-level **API Key management and permission isolation**

> **One-line summary: not an orchestrator — just "cost control + clear visibility".**

````
Before: User calls LLM API directly → spend invisible → month-end shock
After:  User calls via gateway → every call auto-recorded → cost always visible
````

---

## 🧠 Key Highlights

### 1. Zero-invasion gateway proxy

```
User / Agent
    ↓ (just switch the API endpoint)
Your Gateway
    ↓ (auto-record token, latency, cost)
Actual LLM Provider
```

- **No business code changes needed** — just point the API endpoint to the gateway.
- Unified entry for multiple providers and models.
- Supports rate limiting, authentication, and auditability.

### 2. Full-chain cost tracking

- Automatically record input/output token counts per call.
- Automatically calculate cost based on pricing rules (custom price tables supported).
- Aggregate insights by **agent, model, and time range** — see exactly where money goes.

### 3. Budget alerts

- Set budget thresholds (daily / monthly / total), auto-alert when exceeded.
- Supports Webhook push (WeCom, DingTalk, etc.).
- Ideal for team cost governance, project budget caps, and anomaly detection.

### 4. Team-friendly

- Key isolation, permission control, and auditability.
- Supports multi-user, multi-project, multi-environment usage.
- API Keys stored as hashes only, never in plaintext.

### 5. One-click startup

Built-in startup scripts reduce first-run friction:

- Windows: `start.bat`
- Mac/Linux: `start.sh`
- Docker: `docker compose up -d`

> **The more you use it, the clearer it gets.**

---

## ✅ Why This Project is Useful

### Business value

- Turns invisible LLM spend into analyzable data — **no more month-end budget surprises**.
- Unified gateway makes different projects/agents **comparable and auditable**.
- Budget alerts let you **control risk proactively** instead of reviewing after the fact.

### Technical value

- Clean frontend/backend separation for maintainability and extension.
- MySQL + Redis layered storage for business data, caching, and rate limiting.
- Built-in Celery async tasks for scheduled stats, alerting, and background cleanup.
- Docker Compose orchestration to reduce environment setup complexity.

### Practical value

- One-click startup scripts for local demos and quick evaluation.
- Bilingual README for easier team sharing and external communication.
- Built-in screenshots and architecture docs for faster onboarding.

---

## 📸 UI Preview

### 1. Cost Dashboard

One-stop view of cost trends, request volume, and key metric cards. Ideal for daily/weekly review.

![Cost Dashboard](./docs/1.png)

### 2. Cost Analysis

Break down cost by time dimension to quickly locate peaks, drops, and abnormal periods.

![Cost Analysis](./docs/2.png)

### 3. Call Logs

Inspect each LLM call detail — model, latency, tokens, and cost — for issue tracing and accountability.

![Call Logs](./docs/3.png)

### 4. API Key Management

Create isolated keys for teams/projects/environments with permission and rate-limit controls.

![API Key Management](./docs/4.png)

### 5. Pricing Configuration

Maintain model pricing policies and customize billing rules for different providers.

![Pricing Configuration](./docs/5.png)

### 6. Auto Detection

One-click check of provider connectivity to diagnose API address, key, network, and permission issues.

![Auto Detection](./docs/6.png)

### 7. Alert Settings

Define alert rules and get notified when costs exceed thresholds for budget control.

![Alert Settings](./docs/7.png)

---

## 📖 Usage Guide

### Step 1: Install & Start

The repo includes built-in one-click startup scripts:

```bash
# Windows
start.bat

# Mac/Linux
chmod +x start.sh && ./start.sh

# Or use Docker (recommended)
cp .env.example .env
docker compose up -d
```

### Step 2: Log in to the Admin Panel

Access the admin panel and log in with the default admin account:

- URL: `http://localhost:8000/admin/`
- Email: `admin@aimanage.com`
- Password: `admin123456`

> ⚠️ Change the default password in production!

### Step 3: Configure Providers

Add your LLM provider information in the admin panel:

- Provider name
- API base URL
- API Key (stored encrypted)

The system supports one-click auto-detection of provider connectivity.

### Step 4: Create API Keys

Create dedicated API Keys for your agents/projects:

- Set key name (e.g., "Production", "Staging")
- Configure permissions (read/write)
- Set rate limits (requests per minute)

### Step 5: Switch Your Endpoint

Replace the LLM API endpoint in your agent/application with your gateway address:

```
# Before
https://api.openai.com/v1/chat/completions

# After
http://your-gateway/api/gateway/v1/chat/completions
```

### Step 6: Monitor Your Costs

After switching, all calls are automatically recorded. View in the dashboard:

- Real-time cost trends
- Model/Agent distribution
- Call log details
- Alert trigger history

---

## 🧱 Tech Stack Overview

### Frontend

| Type | Technology | Description |
|------|-----------|-------------|
| Framework | React 18 | SPA core |
| Language | TypeScript | Type safety |
| Build | Vite | Fast dev/build workflow |
| Styling | TailwindCSS | Rapid UI development |
| Charts | ECharts | Cost and call trend visualization |
| Routing | React Router | Page routing |
| HTTP | Axios | API communication |

### Backend

| Type | Technology | Description |
|------|-----------|-------------|
| Framework | Django 5 | Main backend framework |
| API | Django REST Framework | RESTful API development |
| Auth | JWT (simplejwt) | Authentication and permissions |
| Gateway | Custom gateway layer | Proxy LLM calls and record traces |
| HTTP | httpx / requests | Upstream request forwarding |
| Token | tiktoken | OpenAI model token counting |
| Encryption | cryptography | API Key encryption at rest |

### Storage & Middleware

| Type | Technology | Description |
|------|-----------|-------------|
| Database | MySQL 8 | Core business data and call logs |
| Cache / Rate Limit | Redis | Performance and request throttling |
| Async Tasks | Celery | Scheduled analytics and alerts |
| Scheduler | django-celery-beat | Periodic task orchestration |

### Deployment & Runtime

| Type | Technology | Description |
|------|-----------|-------------|
| Orchestration | Docker Compose | Unified service startup |
| Reverse Proxy | Nginx | Unified entry routing |
| WSGI Server | Gunicorn | Production-grade Python server |
| Startup Scripts | `start.bat` / `start.sh` | Fast local startup |

---

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│     React 18 + TypeScript + Vite + TailwindCSS   │
├─────────────────────────────────────────────────┤
│               Nginx (Reverse Proxy)              │
│      Route: /api/gateway/* → Gateway             │
│      Route: /api/*        → DRF API              │
│      Route: /*            → React Frontend       │
├─────────────────────────────────────────────────┤
│                  API / Gateway                   │
│  Django 5 + DRF + JWT Auth                       │
│  Gateway: verify key → rate limit → proxy → log  │
├─────────────────────────────────────────────────┤
│                 Async Task Layer                  │
│         Celery Worker + django-celery-beat        │
├─────────────────────────────────────────────────┤
│                   Storage                        │
│        MySQL 8 (data) + Redis (cache/limits)     │
├─────────────────────────────────────────────────┤
│               Deploy / Runtime                   │
│       Docker Compose + Nginx + Gunicorn           │
└─────────────────────────────────────────────────┘
```

---

## 📂 Core File Structure

```text
aimanage/
├── backend/                        # Django backend & gateway
│   ├── config/
│   │   ├── settings.py             # Django global config
│   │   ├── urls.py                 # Root URL routing
│   │   └── celery.py               # Celery config
│   ├── apps/
│   │   ├── users/                  # User module
│   │   ├── gateway/                # LLM gateway (core)
│   │   ├── pricing/                # Pricing management
│   │   ├── stats/                  # Analytics
│   │   └── alerts/                 # Budget alerts
│   ├── utils/
│   │   ├── token_counter.py        # Token counter
│   │   ├── cost_calculator.py      # Cost calculator
│   │   ├── http_client.py          # HTTP proxy client
│   │   ├── encryption.py           # Encryption utils
│   │   └── rate_limiter.py         # Redis rate limiter
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── pages/                  # Page components
│   │   │   ├── Dashboard.tsx       # Cost dashboard (core)
│   │   │   ├── CallLogs.tsx        # Call logs
│   │   │   ├── ApiKeys.tsx         # Key management
│   │   │   ├── Pricing.tsx         # Pricing config
│   │   │   ├── Detection.tsx       # Auto detection
│   │   │   └── Alerts.tsx          # Alert settings
│   │   ├── components/             # Shared components
│   │   ├── api/                    # API request layer
│   │   └── styles/                 # Global styles
│   ├── package.json                # Node dependencies
│   └── Dockerfile
├── nginx/
│   └── nginx.conf                  # Nginx config
├── scripts/
│   ├── init_db.sql                 # DB initialization
│   └── seed_pricing.py             # Pricing seed data
├── docker-compose.yml              # Container orchestration
├── start.bat                       # Windows one-click start
├── start.sh                        # Mac/Linux one-click start
├── .env.example                    # Environment template
├── Makefile                        # Shortcut commands
├── ARCHITECTURE.md                 # Architecture docs
└── sdk/                            # Python SDK (optional)
```

---

## 🚀 Quick Start

### Option A: One-Click Script (Easiest)

```bash
# Windows
Double-click start.bat

# Mac/Linux
chmod +x start.sh && ./start.sh
```

### Option B: Docker Compose (Recommended)

```bash
cp .env.example .env
docker compose up -d
```

After startup:

| Service | URL |
|---------|-----|
| Frontend (Docker) | `http://localhost` |
| Frontend (Script) | `http://localhost:3000` |
| Backend API | `http://localhost:8000/api/` |
| Admin Panel | `http://localhost/admin/` |

### Default Admin Account (Dev Demo)

| Item | Value |
|------|-------|
| Email | `admin@aimanage.com` |
| Password | `admin123456` |

> ⚠️ Always change the default password in production. Use env vars or a secrets manager.

---

## 📦 Requirements

### Base Environment

| Dependency | Min Version | Notes |
|-----------|-------------|-------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build & dev |
| MySQL | 8+ | Primary database |
| Redis | 7+ | Cache & rate limiting (recommended) |
| Docker | 20+ | Container deployment (optional) |
| Docker Compose | v2+ | Container orchestration (optional) |

### Backend Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Django | 5.x | Main framework |
| DRF | 3.16 | RESTful API |
| Celery | 5.x | Async tasks |
| httpx | 0.28+ | HTTP forwarding |
| tiktoken | 0.9+ | Token counting |
| cryptography | 45+ | Key encryption |

Defined in: `backend/requirements.txt`

### Frontend Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool |
| TypeScript | 5.x | Type safety |
| TailwindCSS | 3.x | Styling |
| ECharts | 5.x | Chart visualization |
| React Router | 6.x | Routing |

Defined in: `frontend/package.json`

---

## ❓ FAQ

### Q: Can I run this without Docker?

Yes. The repo includes `start.bat` (Windows) and `start.sh` (Mac/Linux) that automatically check your environment, install dependencies, initialize the database, and start services. You need Python 3.11+, Node.js 18+, and MySQL 8+ installed locally.

### Q: How do I connect my agent?

Simply replace the LLM API endpoint in your agent with your gateway address. No business code changes needed:

```
# Before
https://api.openai.com/v1/chat/completions

# After
http://your-gateway/api/gateway/v1/chat/completions
```

### Q: Which LLM providers are supported?

Through the gateway proxy mode, it supports any OpenAI-compatible provider — OpenAI, Claude, ZhiPu, DeepSeek, Moonshot, and more.

### Q: How accurate is the cost data?

The system supports two data sources: actual token counts returned by the provider (`provider`) and local tiktoken estimation (`estimated`). It prefers provider data and automatically falls back to estimation when unavailable.

### Q: What do I need to change for production?

- Change the default admin password
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use Gunicorn instead of `runserver`
- Enable HTTPS and reverse proxy
- Consider DDoS/WAF protection

### Q: Which alert channels are supported?

Currently Webhook push is supported, compatible with WeCom, DingTalk, and other Webhook-enabled platforms.

---

## ⚠️ Security & Production Notes

- Do not commit real production secrets to the repository.
- Use dedicated database, dedicated Redis, and least-privilege accounts in production.
- For public-facing deployments, consider DDoS/WAF protection, HTTPS, and audit logging.
- Avoid storing sensitive raw fields in logs (tokens, phone numbers, IDs, etc.).
- API Keys are stored as SHA256 hashes only, never in plaintext.

---

## 📜 License

MIT License

---
