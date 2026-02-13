# QUICK START: Frontend Setup Without Node.js

Your system doesn't have Node.js/npm installed yet. Here are your options:

## Option 1: Direct Installation (Recommended) ⭐

### Step 1: Download Node.js
1. Go to https://nodejs.org/
2. Download the **LTS (Long-Term Support)** version (v20.x or later)
3. Run the installer and follow the default prompts
4. **Restart your computer** to update system PATH

### Step 2: Verify Installation
Open PowerShell and run:
```powershell
node --version
npm --version
```

Should show something like:
```
v20.10.0
10.2.4
```

### Step 3: Install Frontend Dependencies
```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
npm install
```

### Step 4: Start Frontend
```powershell
npm run dev
```
Open http://localhost:3000 in your browser.

---

## Option 2: Automated Setup (Windows Only)

Run the provided script:
```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
.\setup.bat
```

The script will:
- Check for Node.js
- Run `npm install`
- Start `npm run dev`

---

## Option 3: Manual Command-by-Command

If you prefer step-by-step control:

```powershell
# Navigate to frontend folder
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"

# Install dependencies (takes 2-5 minutes)
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

---

## Troubleshooting

### "npm: command not found"
- Node.js is not installed or PATH not updated
- **Solution**: Download from https://nodejs.org/ and restart computer

### "npm ERR! code ERESOLVE"
- Dependency version conflict
- **Solution**: Try `npm install --legacy-peer-deps`

### Port 3000 already in use
- Another app is using port 3000
- **Solution**: Kill process or use `npm run dev -- --port 3001`

### Module not found after install
- Dependencies may be missing
- **Solution**: Delete `node_modules/` folder and run `npm install` again

---

## What Gets Installed?

Running `npm install` will:
- Create `node_modules/` folder (~500 MB)
- Install 40+ npm packages including:
  - React 18.2.0
  - Vite 5.0.2 (dev server)
  - Tailwind CSS 3.3.6
  - Axios 1.6.2
  - TypeScript 5.2.2
  - ESLint & Prettier

---

## After Installation

### Available npm Scripts
```powershell
npm run dev      # Start dev server on :3000
npm run build    # Create production build
npm run lint     # Run ESLint
npm run format   # Format with Prettier
npm run preview  # Preview production build
```

### Development Workflow
1. Backend: `python main.py` in backend/ (runs on :8000)
2. Frontend: `npm run dev` in frontend/ (runs on :3000)
3. Access dashboard at http://localhost:3000
4. API requests proxy to http://localhost:8000

---

## Next Steps After Frontend Setup

✅ Frontend dependencies installed
✅ Backend running on http://localhost:8000
✅ Dashboard accessible on http://localhost:3000

**Ready for Phase 2**: Backend API endpoint implementation

---

**Questions?** Check the documentation in `docs/` folder.
