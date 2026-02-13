# Frontend Setup Guide - Phase 1 ✅

## Frontend Project Structure Created

```
frontend/
├── package.json                    # Dependencies & scripts
├── vite.config.js                 # Vite configuration
├── tsconfig.json                  # TypeScript config
├── tailwind.config.js             # Tailwind CSS config
├── postcss.config.js              # PostCSS config
├── .eslintrc.cjs                  # ESLint config
├── .prettierrc                    # Prettier config
├── .env                           # Environment variables
├── index.html                     # Entry HTML
├── src/
│   ├── main.jsx                   # React entry point
│   ├── App.jsx                    # Main app component
│   ├── index.css                  # Global styles + Tailwind
│   ├── components/                # Reusable components
│   │   ├── Dashboard.jsx          # Main dashboard
│   │   ├── Header.jsx             # Top header bar
│   │   ├── FloorStatus.jsx        # Floor occupancy cards
│   │   ├── FloorRecommendation.jsx # Recommended floor display
│   │   ├── EventLog.jsx           # Event history table
│   │   ├── Alert.jsx              # Alert/notification component
│   │   └── index.js               # Component exports
│   ├── services/
│   │   ├── api.js                 # Axios API client setup
│   │   └── floorService.js        # API endpoints for floors & events
│   ├── hooks/
│   │   └── useFetch.js            # Custom hooks for data fetching & polling
│   ├── utils/                     # Utility functions (to be implemented)
│   └── pages/                     # Page components (to be implemented)
└── README.md                      # Frontend docs
```

## Installed Technologies

✅ **React 18.2.0** - UI library
✅ **Vite 5.0** - Build tool & dev server
✅ **Tailwind CSS 3.3.6** - Utility-first CSS
✅ **Axios 1.6** - HTTP client
✅ **Lucide React 0.294** - Icon library
✅ **TypeScript 5.2** - Type safety
✅ **ESLint** - Code linting
✅ **Prettier** - Code formatting

## Installation Steps

### Prerequisites
- **Node.js 18+** and **npm** or **yarn**
- Windows, macOS, or Linux

### Download & Install Node.js

1. Visit https://nodejs.org/
2. Download **LTS version** (18.x or 20.x)
3. Run installer and follow steps
4. Verify installation:
   ```bash
   node --version
   npm --version
   ```

### Install Frontend Dependencies

Once Node.js is installed:

```bash
cd frontend
npm install
```

This will install:
- React & React-DOM
- Vite (build tool)
- Tailwind CSS
- Axios
- TypeScript
- ESLint & Prettier
- And all other dependencies

Installation takes ~2-5 minutes depending on internet speed.

## Running the Frontend

### Development Mode
```bash
npm run dev
```
- Starts Vite dev server on http://localhost:3000
- Hot reload enabled (changes auto-refresh)
- Access dashboard at http://localhost:3000

### Build for Production
```bash
npm run build
```
- Creates optimized production build in `dist/` folder
- Ready for deployment

### Code Quality

Check for linting issues:
```bash
npm run lint
```

Auto-fix issues:
```bash
npm run lint:fix
```

Format code:
```bash
npm run format
```

## Current Features (Demo Mode)

✅ **Dashboard Overview Tab**
- Real-time floor occupancy display
- Floor recommendation system
- Visual progress bars & status indicators

✅ **Event Log Tab**
- Table of recent parking events
- Shows camera ID, vehicle type, direction, timestamp
- Color-coded badges for entry/exit

✅ **Responsive Design**
- Mobile-friendly layout
- Works on desktop, tablet, phone

✅ **Component Library**
- Alert/notification system
- Reusable UI components
- Tailwind styling

## API Integration

Currently using **mock data** for development. Ready to connect to backend APIs:

### API Endpoints to Connect

```
GET  /floors           - Get all floors with occupancy
GET  /recommend        - Get recommended floor
GET  /events           - Get event logs
POST /event            - Submit entry/exit event
```

See [src/services/floorService.js](src/services/floorService.js) for API setup.

## Environment Configuration

File: `.env`
```
VITE_API_URL=http://localhost:8000
```

Change this to point to your backend API.

## Next Steps - Phase 1 Completion

Remaining items for Phase 1:
- [ ] Initialize Git repository
- [ ] Install Node.js and npm
- [ ] Run `npm install` to install dependencies
- [ ] Start frontend with `npm run dev`

Then proceed to Phase 2 (Backend API Implementation)

## Troubleshooting

**npm command not found:**
- Node.js/npm not installed
- Add Node.js to PATH (usually automatic)
- Restart terminal after installation

**Port 3000 already in use:**
- Change port in vite.config.js: `port: 3001`
- Or kill process using port 3000

**Tailwind styles not showing:**
- Run `npm install` again
- Rebuild with `npm run build`
- Clear browser cache

## Architecture

```
Frontend (React + Vite on port 3000)
        ↓
    Axios HTTP Client
        ↓
Backend API (FastAPI on port 8000)
        ↓
    Database (SQLite/PostgreSQL)
```

Vite proxies `/api` requests to backend, so you can use:
```javascript
axios.get('/api/floors')  // Proxied to http://localhost:8000/floors
```
