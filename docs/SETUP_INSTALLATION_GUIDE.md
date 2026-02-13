# SmartPark Setup and Installation Guide

## Prerequisites

- Python `3.10+`
- Node.js `18+`
- npm

## 1. Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend endpoints:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend dashboard:
- `http://localhost:3000`

## 3. Vision Service Setup

```powershell
cd vision
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 4. Quick Local Docker Setup

```powershell
docker compose up --build
```

Optional with vision:
```powershell
docker compose --profile vision up --build
```
