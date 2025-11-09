# Frontend API Key Setup

This guide explains how the frontend securely uses API keys to authenticate with the backend.

## How It Works

The frontend uses a **Next.js API route proxy** to keep the API key secure on the server side:

1. Frontend makes requests to `/api/*` (Next.js API routes)
2. Next.js API route proxy adds the API key header
3. Proxy forwards request to backend API
4. Response is returned to frontend

This ensures the API key is **never exposed to the browser**.

## Setup Instructions

### 1. Configure Environment Variables

Copy the example file:
```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:
```env
# Public API URL (exposed to browser)
NEXT_PUBLIC_API_URL=https://measure-api.onrender.com

# API Key (server-side only - NOT exposed to browser)
API_KEY=Ec0dzulxsDeBxpsVX9dyMO6QdeN6nLj4Evvm-cCAwBQ

# Optional: Set to 'false' to bypass proxy (not recommended)
# NEXT_PUBLIC_USE_API_PROXY=true
```

### 2. How Requests Are Made

The frontend API client automatically routes through the proxy:

**Before (direct call to backend):**
```
Frontend → https://measure-api.onrender.com/v1/companies
          (API key exposed in browser)
```

**After (using proxy):**
```
Frontend → /api/companies
           ↓
           Next.js API Route (adds API key header)
           ↓
           https://measure-api.onrender.com/v1/companies
```

### 3. No Code Changes Required

The existing API client in [lib/api.ts](frontend/lib/api.ts) automatically uses the proxy by default. All your existing code continues to work:

```typescript
import { api } from '@/lib/api'

// This automatically uses the proxy
const companies = await api.getCompanies()
```

## Architecture

### File Structure

```
frontend/
├── app/
│   └── api/
│       └── [...proxy]/
│           └── route.ts          # API proxy that adds API key
├── lib/
│   └── api.ts                    # API client (updated to use proxy)
└── .env.local                    # Environment variables
```

### Proxy Route: `app/api/[...proxy]/route.ts`

This catch-all route:
- Intercepts all `/api/*` requests
- Adds the `X-API-Key` header from server-side env var
- Forwards to the backend API
- Returns the response

Supports all HTTP methods: GET, POST, PUT, PATCH, DELETE

### API Client Updates: `lib/api.ts`

The client now:
- Uses `/api` as base URL by default (proxy mode)
- Can bypass proxy with `NEXT_PUBLIC_USE_API_PROXY=false`
- Handles auth errors gracefully

## Environment Variables

### Server-Side (Secure)
- `API_KEY` - Your backend API key (NOT exposed to browser)

### Client-Side (Public)
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_USE_API_PROXY` - Enable/disable proxy (default: true)

## Security Best Practices

✅ **DO:**
- Keep `API_KEY` in `.env.local` (server-side)
- Add `.env.local` to `.gitignore`
- Use the proxy in production
- Rotate API keys regularly

❌ **DON'T:**
- Use `NEXT_PUBLIC_` prefix for the API key
- Commit API keys to version control
- Disable the proxy in production
- Hardcode API keys in code

## Deployment

### Vercel / Netlify / Other Platforms

Add environment variables in your deployment platform:

1. **API_KEY** = `your-api-key-here` (keep secret)
2. **NEXT_PUBLIC_API_URL** = `https://your-backend.com`

### Docker

Add to your `docker-compose.yml`:

```yaml
services:
  frontend:
    environment:
      - NEXT_PUBLIC_API_URL=https://measure-api.onrender.com
      - API_KEY=${API_KEY}  # From .env file or secrets
```

## Troubleshooting

### "Unauthorized: Invalid or missing API key"

**Check:**
1. `API_KEY` is set in `.env.local`
2. Frontend server was restarted after adding the key
3. API key is valid and active in the backend

### Requests not going through proxy

**Check:**
1. `NEXT_PUBLIC_USE_API_PROXY` is not set to `'false'`
2. Requests are using the `api` client from `@/lib/api`
3. Development server was restarted

### API key exposed in browser

**Check:**
1. You're NOT using `NEXT_PUBLIC_API_KEY`
2. You ARE using the proxy (default behavior)
3. Check browser Network tab - API key should NOT appear

## Development vs Production

### Development (Local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
API_KEY=your-dev-api-key
```

### Production
```env
NEXT_PUBLIC_API_URL=https://measure-api.onrender.com
API_KEY=your-production-api-key
```

**Tip:** Create separate API keys for dev/staging/prod environments.

## Testing the Setup

Run the frontend:
```bash
cd frontend
npm run dev
```

Check the browser console and network tab:
- Requests should go to `/api/companies`, `/api/profiles`, etc.
- The API key should **NOT** appear in request headers (it's added server-side)
- Responses should come back successfully

## Alternative: Direct API Calls (Not Recommended)

If you need to bypass the proxy (e.g., for debugging):

```env
NEXT_PUBLIC_USE_API_PROXY=false
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Warning:** This bypasses API key security. Only use for local development debugging.
