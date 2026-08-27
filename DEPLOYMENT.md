# 🚀 CryptoRecon V4.0 - Deployment Guide

This guide covers how to deploy CryptoRecon (Next.js 14 Frontend + FastAPI Python Backend).

---

## 🌟 Method 1: Recommended Setup (Frontend on Vercel + Backend on Render)

This is the standard and most reliable production setup.

### Step 1: Push Code to GitHub
1. Create a new repository on GitHub (e.g. `cryptorecon-v4`).
2. Push your project code:
   ```bash
   git init
   git add .
   git commit -m "feat: CryptoRecon V4.0 Master Release"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cryptorecon-v4.git
   git push -u origin main
   ```

---

### Step 2: Deploy FastAPI Backend on Render (100% Free)
1. Go to **[render.com](https://render.com)** and sign in.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repo (`cryptorecon-v4`).
4. Configure the settings:
   - **Name**: `cryptorecon-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `ETH_RPC_URL`: `https://eth-mainnet.g.alchemy.com/v2/alch_Jo5yG7u-ZpJpCmRApPS3i`
   - `TRON_API_KEY`: `e6dca6a4-b101-4063-ad89-278127c4dbb7`
   - `ETHERSCAN_API_KEY`: `U2GDDEFNMACMG6HWUEMNKSERPAS36CPUPK`
6. Click **Deploy Web Service**.
7. Copy your live backend URL (e.g., `https://cryptorecon-backend.onrender.com`).

---

### Step 3: Deploy Next.js Frontend on Vercel (100% Free)
1. Go to **[vercel.com](https://vercel.com)** and sign in.
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.
4. In the Project Configuration:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select **`frontend`**.
5. Under **Environment Variables**, add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://cryptorecon-backend.onrender.com` (Your Render Backend URL from Step 2)
6. Click **Deploy**.
7. In ~1 minute, Vercel will give you a live production URL (e.g. `https://cryptorecon.vercel.app`)! 🎉

---

## ⚡ Method 2: All-in-One Direct Vercel Deployment

We have already configured [`vercel.json`](file:///c:/dataaaaa/project/vercel.json) and [`api/index.py`](file:///c:/dataaaaa/project/api/index.py) in the project.

1. Push the root project to GitHub.
2. In Vercel, import the root repo directly (leave Root Directory as `./`).
3. Add Environment Variables on Vercel:
   - `ETH_RPC_URL`: `https://eth-mainnet.g.alchemy.com/v2/alch_Jo5yG7u-ZpJpCmRApPS3i`
   - `TRON_API_KEY`: `e6dca6a4-b101-4063-ad89-278127c4dbb7`
   - `ETHERSCAN_API_KEY`: `U2GDDEFNMACMG6HWUEMNKSERPAS36CPUPK`
4. Click **Deploy**!
