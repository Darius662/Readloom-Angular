# Quick Start - Angular Frontend Development

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd frontend-angular
npm install
```

### Step 2: Start Flask Backend (Terminal 1)
```bash
# From root directory
python Readloom.py
```
Flask runs on: `http://localhost:7227`

### Step 3: Start Angular Frontend (Terminal 2)
```bash
# From frontend-angular directory
npm start
```
Angular runs on: `http://localhost:4200`

---

## 📋 What's Ready

✅ Angular 18+ project initialized  
✅ Standalone components configured  
✅ Routing with lazy loading  
✅ TypeScript strict mode  
✅ Bootstrap 5 + TailwindCSS  
✅ Flask CORS enabled  
✅ Development environment ready  

---

## 📁 Project Structure

```
frontend-angular/
├── src/app/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page-level components
│   ├── services/      # API & business logic (create in Phase 2)
│   ├── models/        # TypeScript interfaces (create in Phase 2)
│   ├── app.routes.ts  # Route configuration
│   └── app.component.ts
├── src/environments/  # Environment configs
├── src/styles.css    # Global styles
├── package.json      # Dependencies
└── angular.json      # Angular config
```

---

## 🔗 API Configuration

**Development**: `http://localhost:7227/api`  
**Production**: `/api` (relative)

Edit in: `src/environments/environment.ts`

---

## 📚 Documentation

- **`ANGULAR_SETUP.md`** - Complete setup guide
- **`docs/ANGULAR_MIGRATION_SETUP.md`** - Architecture & migration details
- **`frontend-angular/README.md`** - Project-specific README
- **`PHASE_1_COMPLETION_SUMMARY.md`** - What was completed

---

## 🛠️ Common Commands

```bash
# Development
npm start                    # Start dev server

# Building
npm run build               # Development build
npm run build:prod          # Production build

# Testing
npm test                    # Unit tests
npm run e2e                 # E2E tests

# Code Quality
npm run lint                # Lint code
```

---

## ⚠️ Troubleshooting

### Port 4200 in use?
```bash
ng serve --port 4300
```

### CORS errors?
- Verify Flask is running on port 7227
- Check `backend/internals/server.py` for CORS config
- Verify API URL in `src/environments/environment.ts`

### Module not found?
```bash
npm install
npm cache clean --force
```

---

## 📝 Next Phase (Phase 2)

Create core services:
- `src/app/services/api.service.ts` - HTTP client
- `src/app/services/auth.service.ts` - Authentication
- `src/app/services/notification.service.ts` - User notifications
- `src/app/models/` - TypeScript interfaces

---

## 🎯 Current Status

**Phase 1**: ✅ COMPLETE  
**Phase 2**: Ready to start  
**Total Phases**: 9

---

## 💡 Tips

- Use `ng generate component` to create components
- Use `ng generate service` to create services
- Check browser DevTools (F12) for API calls
- Enable Angular DevTools extension for debugging
- Keep components focused and reusable

---

## 📞 Need Help?

1. Check `ANGULAR_SETUP.md` for detailed guide
2. Review `docs/ANGULAR_MIGRATION_SETUP.md` for architecture
3. Check Flask logs for API errors
4. Check browser console for frontend errors
5. Review Network tab in DevTools for API calls

---

**Happy coding! 🎉**
