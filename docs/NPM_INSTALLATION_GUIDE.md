# 🔧 Frontend Dependencies Installation Guide

## Current Status: Node.js NOT Installed

Node.js and npm are required to install frontend dependencies.

---

## Installation Steps

### Step 1: Download Node.js

1. Visit: https://nodejs.org/
2. Click **LTS** (Long Term Support) button
3. Download the Windows installer (.msi)
4. Current recommended version: **20.x LTS**

### Step 2: Install Node.js

1. Run the downloaded `.msi` installer
2. Follow the installation wizard
3. Accept the default installation path: `C:\Program Files\nodejs\`
4. **Important**: Accept option to install npm package manager
5. Let it install necessary tools
6. **Restart your computer** after installation completes

### Step 3: Verify Installation

Open PowerShell and run:
```powershell
node --version    # Should show v20.x or higher
npm --version     # Should show 9.x or higher
```

### Step 4: Install Frontend Dependencies

After Node.js is installed and you've restarted:

```powershell
cd "d:\Kanishk\PROJECT\SMART PARKING\frontend"
npm install
```

This will:
- Download and install all npm packages
- Create `node_modules` folder (~500 MB)
- Install React, Vite, Tailwind CSS, Axios, etc.
- Create `package-lock.json` for reproducible installs

Installation time: 2-5 minutes (depends on internet speed)

### Step 5: Start Frontend Dev Server

```powershell
npm run dev
```

The server will start on: http://localhost:3000

---

## What Gets Installed

### Core Dependencies
- React 18.2.0 - UI framework
- Vite 5.0.2 - Build tool & dev server
- Tailwind CSS 3.3.6 - CSS utility framework
- Axios 1.6.2 - HTTP client
- Lucide React 0.294 - Icon library

### Development Dependencies
- TypeScript 5.2.2 - Type safety
- ESLint 8.53.0 - Code linting
- Prettier 3.1.0 - Code formatting
- PostCSS & Autoprefixer - CSS processing

**Total Dependencies**: 40+ packages

---

## Troubleshooting

### "npm: The term 'npm' is not recognized"
- Node.js not installed
- Download and install from https://nodejs.org/
- Restart PowerShell/Computer
- Try again

### "command not found: npm"
- Node.js PATH not set
- Restart your computer after installation
- Or add Node.js to PATH manually

### npm install is slow
- Normal on first install
- Can take 5-10 minutes on slower connections
- Check: `npm config get registry` (should be https://registry.npmjs.org/)

### Port 3000 already in use
- Change port in `vite.config.js`:
  ```javascript
  port: 3001
  ```
- Or kill the process using port 3000

### node_modules folder is too large
- Normal - npm packages are ~500 MB for this project
- Can be ignored in git with `.gitignore`

---

## Next Steps

1. **Install Node.js** from https://nodejs.org/
2. **Restart your computer**
3. **Run npm install** in frontend folder
4. **Run npm run dev**
5. **Open http://localhost:3000**

---

## npm Commands Reference

```bash
npm install              # Install all dependencies (first time)
npm install <package>   # Install specific package
npm run dev             # Start development server
npm run build           # Build for production
npm run preview         # Preview production build
npm run lint            # Check code quality
npm run lint:fix        # Fix linting issues
npm run format          # Format code with Prettier
npm cache clean --force # Clear npm cache if issues
npm list                # List installed packages
```

---

## Verification Checklist

- [ ] Node.js installed (verify: `node --version`)
- [ ] npm installed (verify: `npm --version`)
- [ ] Restarted computer/terminal after Node.js install
- [ ] `npm install` completed successfully
- [ ] No errors in npm output
- [ ] `node_modules` folder exists and has files
- [ ] `npm run dev` starts without errors
- [ ] Dashboard loads at http://localhost:3000

---

**After Node.js installation, run `npm install` to complete frontend setup!**
