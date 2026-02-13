# Phase 1 Installation & Startup Checklist

## Backend ✅ (Already Installed & Running)

### Verify Backend is Running:
```powershell
# Check if server is still running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","project":"SmartPark API"}
```

### Backend Paths:
- **Code**: `d:\Kanishk\PROJECT\SMART PARKING\backend\`
- **Main file**: `backend\main.py`
- **API docs**: http://localhost:8000/docs
- **Database**: `backend\smartpark.db` (SQLite)

---

## Frontend ⏳ (Requires Node.js Installation)

### Step 1: Install Node.js (One-time)

1. **Download Node.js 18+ LTS** from https://nodejs.org/
   - Choose "LTS" version
   - Windows installer (.msi)

2. **Install Node.js**:
   - Run downloaded `.msi` file
   - Accept default settings
   - **Restart your computer/terminal** after installation

3. **Verify Installation**:
   ```powershell
   node --version    # Should show v18.x or v20.x
   npm --version     # Should show 9.x or 10.x
   ```

### Step 2: Install Frontend Dependencies (One-time)

```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
npm install
```

This will take 2-5 minutes. It installs:
- React, Vite, Tailwind CSS, Axios
- All development tools (ESLint, Prettier, TypeScript)

### Step 3: Start Frontend Dev Server

```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
npm run dev
```

Server will start on **http://localhost:3000**

---

## Running Everything (After Initial Setup)

### Terminal 1 - Backend (if not still running):
```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\backend"
python -m uvicorn main:app --reload
# Backend runs on http://localhost:8000
```

### Terminal 2 - Frontend:
```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
npm run dev
# Frontend runs on http://localhost:3000
```

### Terminal 3 - Optional (Vision Service later):
```powershell
# To be configured in Phase 4
```

---

## Access the Dashboard

1. **Open browser**: http://localhost:3000
2. **Dashboard tabs**:
   - 📊 **Overview**: Floor occupancy and recommendations
   - 📋 **Event Log**: Parking entry/exit history
3. **API Docs** (Backend): http://localhost:8000/docs

---

## Project Structure Ready

```
d:\Kanishk\PROJECT\SMART PARKING\
│
├── backend/                    ✅ Running on :8000
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── smartpark.db
│
├── frontend/                   ⏳ Install npm packages
│   ├── src/
│   │   ├── components/        (6 components ready)
│   │   ├── services/          (API client)
│   │   ├── hooks/             (useFetch, usePolling)
│   │   └── App.jsx
│   ├── package.json
│   └── node_modules/          (After npm install)
│
├── vision/                     (Phase 4 setup later)
│
└── Documentation/              ✅ Complete
    ├── TODO_LIST.md
    ├── PHASE_1_COMPLETE.md
    ├── PHASE_1_SUMMARY.md
    ├── FRONTEND_COMPONENTS.md
    └── This file
```

---

## Troubleshooting

### Frontend won't start after `npm install`:
1. Delete `node_modules` folder
2. Run `npm install` again
3. Check Node.js version: `node --version` (should be 18+)

### Port already in use:
**Error**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solution**:
```powershell
# Find process using port 3000
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

# Kill it:
Stop-Process -Id <PID> -Force

# Or change port in vite.config.js: port: 3001
```

### Backend API not responding:
```powershell
# Check if backend is running:
curl http://localhost:8000/health

# If not, start it:
cd backend
python -m uvicorn main:app --reload
```

### React components not showing styles:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Rebuild: `npm run build && npm run preview`
3. Check Tailwind config: `tailwind.config.js`

---

## Next: Phase 2 Backend API

After everything is running, proceed to Phase 2 to implement:
- ✅ Database models (already done)
- [ ] Core API endpoints:
  - POST `/event` (submit parking events)
  - GET `/floors` (get floor status)
  - GET `/recommend` (get best floor)
  - GET `/events` (get event logs)
- [ ] Event idempotency logic
- [ ] Database transactions

See `TODO_LIST.md` Phase 2 for full breakdown.

---

## Current Status

| Component | Status | Port |
|-----------|--------|------|
| Backend (FastAPI) | ✅ Running | 8000 |
| Frontend (React) | ⏳ Ready to install | 3000 |
| Database (SQLite) | ✅ Ready | Local file |
| Vision Service | ⏳ Phase 4 | Future |
| Documentation | ✅ Complete | - |

---

## Verification Steps

### Verify Backend:
```bash
# Should return healthy status
curl http://localhost:8000/health
```

### Verify Frontend (after npm install):
```bash
npm run build
# Should create dist/ folder without errors
```

### Verify Database:
```bash
# SQLite file exists
dir backend\smartpark.db
```

---

## Quick Commands Reference

```powershell
# Start backend
cd backend && python -m uvicorn main:app --reload

# Install frontend (one-time)
cd frontend && npm install

# Start frontend
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build

# Check Node.js version
node --version

# Check npm version
npm --version

# Clear npm cache if issues
npm cache clean --force
```

---

## Support Files

For detailed information:
- 📄 [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Backend details
- 📄 [PHASE_1_FRONTEND_SETUP.md](PHASE_1_FRONTEND_SETUP.md) - Frontend setup
- 📄 [PHASE_1_SUMMARY.md](PHASE_1_SUMMARY.md) - Full summary
- 📄 [FRONTEND_COMPONENTS.md](FRONTEND_COMPONENTS.md) - Components docs
- 📄 [backend/README.md](backend/README.md) - Backend docs
- 📄 [frontend/README.md](frontend/README.md) - Frontend docs

---

## ✅ Phase 1 Complete!

**Backend**: Ready ✅
**Frontend**: Ready to install ⏳
**Documentation**: Complete ✅
**Database Models**: Ready ✅
**Project Structure**: Ready ✅

**Next Step**: Install Node.js and npm packages, then start frontend!
