# 📁 Fantasy Trade Analyzer - Project Structure

## 🎯 Overview
```
FP_Tensorflow/
├── backend/                    # Python FastAPI server
├── fantasy-trade-app/          # React frontend application
├── README.md                   # Main project documentation
├── CHANGELOG.md               # Development progress log
├── PROJECT_STRUCTURE.md       # This file
└── .gitignore                 # Git ignore rules
```

## 🐍 Backend (`/backend`)

### **Core Files**
```
backend/
├── simple_main.py             # FastAPI server & API endpoints
├── espn_service.py            # ESPN API integration service
├── requirements.txt           # Python dependencies
├── venv/                      # Virtual environment (excluded from git)
└── __pycache__/              # Python cache (excluded from git)
```

### **Key Components**

#### **`simple_main.py`** - Main API Server
- FastAPI application setup
- CORS configuration for React frontend
- API endpoint definitions:
  - `POST /api/connect` - League connection
  - `GET /api/teams` - Team listings  
  - `POST /api/select-team` - Team selection
  - `GET /api/roster/{team_id}` - Detailed roster data
  - `POST /api/analyze-trade` - Trade analysis
  - `GET /api/health` - Health check

#### **`espn_service.py`** - ESPN Integration
- ESPN API wrapper and authentication
- Player data parsing and normalization
- Trade analysis algorithms
- League and team data management
- Error handling and logging

---

## ⚛️ Frontend (`/fantasy-trade-app`)

### **Project Structure**
```
fantasy-trade-app/
├── public/                    # Static assets
│   ├── index.html            # Main HTML template
│   ├── favicon.ico           # Site icon
│   └── manifest.json         # PWA manifest
├── src/                      # React application source
│   ├── components/           # Reusable React components
│   ├── context/             # React Context providers
│   ├── pages/               # Page-level components
│   ├── App.js               # Main application component
│   ├── index.js             # Application entry point
│   └── index.css            # Global styles
├── package.json             # Node.js dependencies & scripts
├── tailwind.config.js       # Tailwind CSS configuration
└── node_modules/            # Node dependencies (excluded from git)
```

### **Component Architecture**

#### **Core Components (`/src/components`)**
```
components/
├── Header.js                 # Navigation header with branding
├── Dashboard.js              # Main league overview page
├── LeagueConnect.js          # ESPN league connection flow
├── TradeAnalyzer.js          # Main trade analysis interface
├── TradeVisualization.js     # Interactive trade comparison charts
└── Roster.js                 # Detailed team roster display
```

#### **Pages (`/src/pages`)**
```
pages/
└── RosterPage.js             # Full-page roster view
```

#### **Context (`/src/context`)**
```
context/
└── LeagueContext.js          # Global state management for league data
```

---

## 🎨 Design System

### **Styling Architecture**
- **Tailwind CSS**: Utility-first CSS framework
- **Component-based styling**: Consistent design patterns
- **Responsive design**: Mobile-first approach
- **Color theming**: Blue/green team separation

### **Key Design Elements**
- **Gradients**: Modern visual appeal
- **Card layouts**: Clean information organization
- **Hover animations**: Interactive feedback
- **Professional typography**: Clear hierarchy

---

## 🔧 Current Implementation Status

### **✅ Completed Features**
- ESPN API integration with authentication
- Real-time player data parsing
- Trade analysis engine
- Visual trade comparisons
- Professional UI with responsive design
- Side-by-side team comparison interface

### **🏗️ Architecture Highlights**
- **Backend**: FastAPI with ESPN API wrapper
- **Frontend**: React with Context state management
- **Styling**: Tailwind CSS with custom components
- **Data Flow**: RESTful API communication

---

## 📊 Code Statistics

### **Backend**
- **Files**: 2 main Python files (~800 lines)
- **API Endpoints**: 6 RESTful endpoints
- **Dependencies**: FastAPI, ESPN-API, Uvicorn

### **Frontend**
- **Components**: 8+ React components (~1,700+ lines)
- **Pages**: 2 page-level components
- **Dependencies**: React, Tailwind CSS, React Router

---

## 🚀 Development Workflow

### **Running the Application**
1. **Backend**: `cd backend && python simple_main.py` (Port 8000)
2. **Frontend**: `cd fantasy-trade-app && npm start` (Port 3000)

### **Key Development Decisions**
- **React Context** for simple state management
- **Component-based architecture** for maintainability
- **Tailwind CSS** for rapid UI development
- **FastAPI** for modern Python backend

---

This structure represents a complete, functional fantasy football trade analyzer with professional UI and comprehensive ESPN integration.
