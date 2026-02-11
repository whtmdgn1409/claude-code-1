# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**딜모아 (DealMoa)** - Hot Deal Aggregation and Notification Service

A Korean hot deal aggregator service that:
- Collects real-time hot deal information from major Korean communities
- Provides integrated listings with smart filtering
- Sends personalized keyword-based push notifications
- Target users: Smart consumers (20-40 age group) seeking best prices
- Platforms: Mobile app (Android/iOS) and mobile web

**Tech Stack**:
- Backend: Python + FastAPI
- Mobile: React Native
- Database: PostgreSQL
- Cache/Queue: Redis

## Core Architecture (Planned)

### System Components

1. **Multi-Source Crawler**
   - Target sites: 뽐뿌 (Ppomppu), 루리웹 (Ruliweb), 펨코 (Fmkorea), 퀘이사존 (Quasarzone), 딜바다 (Dealbada)
   - Real-time scraping with data normalization
   - Shopping mall link parsing and thumbnail extraction

2. **Data Processing Layer**
   - Price extraction and historical comparison (price signal light: 🟢역대가 / 🟡평균가 / 🔴비쌈)
   - Hot Level calculation based on upvotes, comments, and view velocity
   - AI-powered 3-line summary of post and comments
   - Category auto-classification
   - Blacklist filtering (spam, advertisers)

3. **User Personalization**
   - Social login (Kakao, Google, Apple)
   - Interest keywords (up to 20)
   - Exclusion keywords (NOT conditions)
   - Bookmark system

4. **Notification Engine**
   - Real-time push within 1 minute of keyword match
   - Do Not Disturb mode (23:00-07:00)
   - Demographic-based recommendations (optional)

### UI/UX Requirements

- **Feed Style**: Vertical scroll card-based UI (Instagram/Karrot Market style)
- **Visual Hierarchy**: Large images, prominent pricing
- **Community Badges**: Color-coded source indicators
- **Performance**: Caching required for instant loading

## Feature Priority

**MVP (Phase 1)**:
- Multi-site crawling
- Integrated listing view
- Keyword push notifications

**Enhancement (Phase 2)**:
- Price comparison with historical data
- AI comment summarization
- Automatic categorization

**Expansion (Phase 3)**:
- Demographic-based recommendation algorithm
- Community features (user discussions)

## Key Korean Context

- Service targets Korean market with Korean language content
- Integrates with major Korean deal communities
- Uses Korean social login providers (Kakao prominent)
- All UI/content will be in Korean

## Development Commands

### Local Environment Setup

**Start databases (required first):**
```bash
docker-compose up -d
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # First time only
uvicorn app.main:app --reload
```
- API runs at http://localhost:8000
- API docs: http://localhost:8000/docs

**Mobile:**
```bash
cd mobile
npm install
cp .env.example .env  # First time only
npm run ios     # iOS (macOS only)
npm run android # Android
```

### Testing & Quality

**Backend:**
```bash
cd backend
pytest                    # Run tests
black app/               # Format code
flake8 app/              # Lint check
```

**Mobile:**
```bash
cd mobile
npm test                 # Run tests
npm run lint            # Lint check
```

## Project Structure

```
backend/app/
├── main.py              # FastAPI app entry point
├── api/                 # API route handlers
├── models/              # SQLAlchemy database models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── crawlers/            # Site-specific crawlers (ppomppu, ruliweb, etc.)
└── utils/               # Helper utilities

mobile/src/
├── screens/             # Screen components (Home, Detail, Settings)
├── components/          # Reusable UI components (DealCard, etc.)
├── navigation/          # React Navigation setup
├── services/            # API client
└── store/               # State management
```
