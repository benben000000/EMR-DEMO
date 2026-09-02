# Vercel Deployment Guide for G1 Health EMR

This project is fully ready for zero-configuration deployment on **[Vercel](https://vercel.com/)**.

---

## 1-Click Deployment via Vercel Dashboard

1. **Log in to Vercel**:
   Go to [https://vercel.com](https://vercel.com) and sign in with your GitHub account (`benben000000`).

2. **Import Git Repository**:
   - Click **`Add New...`** &rarr; **`Project`**.
   - Find and select **`EMR-DEMO`** (or `benben000000/EMR-DEMO`).

3. **Configure Project**:
   - **Framework Preset**: *Other* (detected automatically via `vercel.json`).
   - **Root Directory**: `./` (Default).
   - **Build Command**: *None needed* (Serverless Python & static assets are bundled automatically).
   - **Output Directory**: *Default*.

4. **Deploy**:
   - Click **`Deploy`**.
   - In ~30-45 seconds, Vercel will produce a live HTTPS URL (e.g., `https://emr-demo-benben.vercel.app`).

---

## Project Structure for Vercel

```
EMR-DEMO/
├── api/
│   └── index.py            # Vercel Serverless Python entrypoint (handles / and /dashboard)
├── public/                 # Static CDN assets
│   ├── index.html          # Static Login Page fallback
│   ├── dashboard.html      # Static Dashboard fallback
│   └── Personalization/
│       └── logos/          # Brand logos & favicon
├── vercel.json             # Vercel routing, builds & serverless config
├── requirements.txt        # Python dependency manifest (zero external bloat)
└── serve_demo.py           # Local development server (port 5000)
```

---

## Deployment via Vercel CLI (Optional)

If you have Node.js / npm installed locally or on your CI/CD runner:

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Authenticate
vercel login

# 3. Deploy to Production
vercel --prod
```

---

## Credentials on Live Site
- **Username**: `admin`
- **Password**: `pass123`
