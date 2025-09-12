# 🚀 CVF API Quick Start Guide

## Option 1: Python Run Script (Recommended)

```bash
cd src
python run.py
```

**Available options:**
```bash
python run.py --help                    # Show all options
python run.py                          # Start server (default: localhost:8000)
python run.py --host 0.0.0.0 --port 3000  # Custom host/port
python run.py --test                   # Run API tests
python run.py --setup-only            # Just setup, don't start server
python run.py --no-reload             # Disable auto-reload
```

## Option 2: Bash Script

```bash
cd src
./run.sh                              # Start server
./run.sh --test                       # Run tests
./run.sh --port 3000                  # Custom port
```

## Option 3: Manual Setup

```bash
cd src
pip install -r requirements.txt       # Install dependencies
python init_db.py                     # Setup database
uvicorn main:app --reload             # Start server
```

## 📊 What Happens Automatically

1. **✅ Dependency Check** - Verifies all packages are installed
2. **📝 Environment Setup** - Creates `.env` from template with SQLite config
3. **🗄️ Database Init** - Creates tables and loads sample data
4. **🚀 Server Start** - Launches FastAPI with auto-reload

## 🌐 Access Points

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

```bash
python run.py --test                  # Full test suite
curl http://localhost:8000/health     # Quick health check
```

## 📁 Sample Data Included

- **3 Companies**: Acme Corp, TechStart Inc, GrowthCo
- **Cohorts**: Monthly S&M spend plans
- **Payments**: Customer payment histories
- **Trades**: Investment terms and caps
- **Thresholds**: Performance benchmarks

## 🔧 Configuration

Edit `.env` file for custom settings:
```env
DATABASE_URL=sqlite:///./cvf.db       # Local SQLite (default)
# DATABASE_URL=postgresql://...       # Supabase for production
ENVIRONMENT=development
```

## 🆘 Troubleshooting

**Port already in use?**
```bash
python run.py --port 3000
```

**Database issues?**
```bash
rm cvf.db                             # Delete SQLite file
python run.py --setup-only            # Reinitialize
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**Test failures?**
```bash
python run.py --test                  # See detailed output
```

## 🎯 Next Steps

1. **✅ Start the API** with one of the run commands above
2. **🌐 Open http://localhost:8000/docs** to explore the API
3. **🧪 Run tests** to verify everything works
4. **🎨 Build frontend** using the Lovable prompts in your canvas
5. **☁️ Deploy** to Supabase for production

---

*Need help? Check `README_IMPLEMENTATION.md` for detailed documentation.*