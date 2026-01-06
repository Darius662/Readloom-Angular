# Readloom Angular Frontend

Modern Angular 21 frontend for the Readloom manga/comics collection manager.

## Prerequisites

- Node.js 20+ (LTS recommended)
- npm 10+
- Angular CLI 21+

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your Flask backend URL if different from default.

## Development

Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

The dev server will automatically reload when you modify source files.

## Build

Build for production:
```bash
npm run build:prod
```

The build artifacts will be stored in the `dist/` directory.

## Testing

Run unit tests:
```bash
npm test
```

Run E2E tests:
```bash
npm run e2e
```

## Code Quality

Lint the code:
```bash
npm run lint
```

## Project Structure

```
src/
├── app/
│   ├── components/          # Reusable components
│   │   ├── header/          # App header with toolbar
│   │   └── sidebar/         # Navigation sidebar
│   ├── pages/               # Page components
│   │   ├── dashboard/
│   │   ├── library/
│   │   ├── calendar/
│   │   ├── collections/
│   │   ├── authors/
│   │   └── settings/
│   ├── services/            # API and business logic services
│   ├── models/              # TypeScript interfaces/models
│   ├── app.component.ts     # Root component
│   ├── app.routes.ts        # Route configuration
│   └── app.component.html   # Root template
├── styles.scss              # Global styles and theming
├── index.html               # HTML entry point
└── main.ts                  # Application bootstrap
docs/
└── THEMING.md               # Theming documentation
```

## Theming

The app uses Angular Material 21 with CSS custom properties for theming. See [docs/THEMING.md](docs/THEMING.md) for details on:

- Angular Material 21 theme configuration
- CSS custom properties for theme-aware components
- ThemeService for runtime light/dark mode switching
- Writing theme-aware component styles

## API Integration

The frontend communicates with the Flask backend API at `http://localhost:7227/api`.

### Key API Endpoints

- `GET /api/series` - List all series
- `GET /api/collections` - List all collections
- `GET /api/authors` - List all authors
- `GET /api/calendar` - Calendar events
- `POST /api/series` - Create new series
- `PUT /api/series/:id` - Update series
- `DELETE /api/series/:id` - Delete series

See the Flask backend documentation for complete API reference.

## Development Workflow

1. Create a new feature branch
2. Make changes to components/services
3. Test locally with `npm start`
4. Run tests: `npm test`
5. Build for production: `npm run build:prod`
6. Commit and push changes

## Troubleshooting

### Port 4200 already in use
```bash
ng serve --port 4300
```

### CORS errors when calling API
Ensure Flask backend has CORS enabled and is running on the correct port (default: 7227).

### Module not found errors
Run `npm install` to ensure all dependencies are installed.

## Contributing

Follow Angular style guide and best practices:
- Use standalone components
- Use CSS custom properties for theme-aware styling (see [docs/THEMING.md](docs/THEMING.md))
- Implement proper error handling
- Add unit tests for new features
- Keep components focused and reusable

## License

MIT License - See LICENSE file for details
