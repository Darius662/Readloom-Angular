# Phase 4: Deployment Guide

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Build Docker Image

```bash
# Build the production Angular bundle
cd frontend-angular
npm run build:prod

# Build Docker image
docker build -t readloom:latest .

# Run container
docker run -p 4200:4200 readloom:latest
```

#### Docker Compose (Full Stack)

```bash
# From root directory
docker-compose up -d

# Verify services running
docker-compose ps

# View logs
docker-compose logs -f
```

Services:
- Angular frontend: http://localhost:4200
- Flask backend: http://localhost:7227

### Option 2: Netlify Deployment

#### Prerequisites
- Netlify account
- GitHub repository connected

#### Deploy Steps

1. **Build locally first**
```bash
cd frontend-angular
npm run build:prod
```

2. **Deploy using Netlify CLI**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist/readloom-angular
```

3. **Or use Git integration**
- Push to GitHub
- Netlify auto-deploys on push

#### Netlify Configuration

Create `netlify.toml`:
```toml
[build]
  command = "npm run build:prod"
  publish = "dist/readloom-angular"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Option 3: Vercel Deployment

#### Deploy Steps

```bash
npm install -g vercel
vercel --prod
```

#### Vercel Configuration

Create `vercel.json`:
```json
{
  "buildCommand": "npm run build:prod",
  "outputDirectory": "dist/readloom-angular",
  "env": {
    "NODE_VERSION": "18"
  }
}
```

### Option 4: Traditional Server Deployment

#### Prerequisites
- Node.js 18+ installed
- PM2 for process management

#### Deploy Steps

1. **Build production bundle**
```bash
cd frontend-angular
npm run build:prod
```

2. **Copy to server**
```bash
scp -r dist/readloom-angular user@server:/var/www/readloom/
```

3. **Setup Nginx**
```nginx
server {
    listen 80;
    server_name readloom.example.com;

    root /var/www/readloom/dist/readloom-angular;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:7227;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

4. **Restart Nginx**
```bash
sudo systemctl restart nginx
```

## Environment Configuration

### Development
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:7227/api',
  wsUrl: 'ws://localhost:7227'
};
```

### Production
```typescript
// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.readloom.example.com/api',
  wsUrl: 'wss://api.readloom.example.com'
};
```

## Pre-Deployment Checklist

### Code Quality
- [ ] All TypeScript errors resolved
- [ ] No console errors in DevTools
- [ ] Linting passes (`npm run lint`)
- [ ] No unused imports or variables
- [ ] Code follows Angular style guide

### Testing
- [ ] Manual testing completed
- [ ] All pages tested on desktop
- [ ] All pages tested on mobile
- [ ] Dark mode tested
- [ ] API integration verified
- [ ] Error handling tested

### Performance
- [ ] Production build < 500KB
- [ ] Lazy loading configured
- [ ] Images optimized
- [ ] No memory leaks
- [ ] Load time < 3 seconds

### Security
- [ ] CORS properly configured
- [ ] No hardcoded secrets
- [ ] Environment variables used
- [ ] HTTPS enabled in production
- [ ] CSP headers configured

### Documentation
- [ ] README updated
- [ ] API documentation complete
- [ ] Deployment guide created
- [ ] Environment setup documented
- [ ] Troubleshooting guide created

## Post-Deployment Verification

### Health Checks

```bash
# Check frontend loads
curl https://readloom.example.com

# Check API accessible
curl https://readloom.example.com/api/series

# Check CORS headers
curl -H "Origin: https://readloom.example.com" \
     -H "Access-Control-Request-Method: GET" \
     https://api.readloom.example.com/api/series
```

### Monitoring

1. **Error Tracking**
   - Setup Sentry for error monitoring
   - Configure alerts for critical errors

2. **Performance Monitoring**
   - Use Google Analytics
   - Monitor Core Web Vitals
   - Track API response times

3. **Uptime Monitoring**
   - Setup UptimeRobot
   - Configure alerts for downtime

## Rollback Plan

### If Deployment Fails

1. **Revert to Previous Version**
```bash
# Using Docker
docker pull readloom:previous
docker run -p 4200:4200 readloom:previous

# Using Git
git revert <commit-hash>
npm run build:prod
```

2. **Check Logs**
```bash
# Docker logs
docker logs <container-id>

# Server logs
tail -f /var/log/nginx/error.log
```

3. **Notify Users**
- Post status update
- Provide ETA for fix
- Document issue for post-mortem

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Deploy multiple instances
- Use CDN for static assets

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Cache frequently accessed data

### CDN Setup
```nginx
# CloudFlare or similar
- Cache static assets
- Enable gzip compression
- Setup caching rules
```

## Maintenance

### Regular Tasks
- [ ] Monitor error logs weekly
- [ ] Review performance metrics
- [ ] Update dependencies monthly
- [ ] Security patches as needed
- [ ] Backup database regularly

### Update Process
1. Test updates in staging
2. Deploy to production
3. Monitor for errors
4. Document changes in CHANGELOG

## Disaster Recovery

### Backup Strategy
- Daily database backups
- Weekly code backups
- Monthly full system backups
- Test restore procedures

### Recovery Procedures
1. Restore from latest backup
2. Verify data integrity
3. Test all functionality
4. Notify users of recovery

## Support & Troubleshooting

### Common Issues

**Issue**: White screen on load
- Check browser console for errors
- Verify API URL correct
- Check CORS headers

**Issue**: API 404 errors
- Verify Flask backend running
- Check API endpoint exists
- Verify CORS configured

**Issue**: Slow load times
- Check bundle size
- Enable gzip compression
- Use CDN for assets
- Optimize images

**Issue**: Dark mode not working
- Check LocalStorage available
- Verify theme service initialized
- Check CSS variables defined

## Contact & Support

- **Issues**: GitHub Issues
- **Documentation**: /docs
- **API Docs**: /api/docs
- **Support Email**: support@readloom.example.com
