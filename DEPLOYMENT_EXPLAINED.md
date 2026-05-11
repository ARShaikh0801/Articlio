# Django Deployment: Gunicorn & Workers Explained 🚀

This guide explains how your website actually runs on the internet and how to handle more visitors in the future.

---

## 1. What is Gunicorn? (The Professional Bridge) 🌉
**Gunicorn** (Green Unicorn) is the "bridge" between the internet and your Django code.

- **The Problem:** Web browsers speak "HTTP," but Django speaks "Python."
- **The Solution:** Gunicorn acts as a translator. It takes requests from the browser, translates them for Django, and sends the answer back.
- **Why use it?** The `runserver` command you use locally is like a small home toaster—it's only for testing. Gunicorn is like an industrial kitchen—built for speed, security, and stability.

---

## 2. Workers: The Chefs in the Kitchen 👨‍🍳
Gunicorn manages **Workers**. Think of a worker as a **Chef**.

- **Single Worker (1 Chef):** Your current setup. If two people visit at the exact same microsecond, Chef handles person A first, then person B.
- **Multi-Worker (Multiple Chefs):** If you have 3 workers, you have 3 chefs. They can handle 3 people simultaneously.

### The Formula for Scaling
In the professional world, the standard formula for workers is:
`Workers = (2 × Number of CPU Cores) + 1`

So if you have a server with 2 CPU cores, you should use **5 workers**.

---

## 3. Scaling in the Future 📈
To scale your app when you get thousands of visitors, you change your "Start Command."

**Currently (1 Worker):**
`gunicorn Articlio.wsgi:application`

**Future (e.g., 4 Workers):**
`gunicorn -w 4 Articlio.wsgi:application`

---

## 4. Platform Limits: Render vs. Railway 🏗️

### Render (Free Tier)
- **RAM Limit:** 512 MB.
- **Worker Limit:** Usually **1 worker**. 
- **The Risk:** Every worker uses ~150-200MB of RAM. If you try to run 3 workers on Render Free, your total memory will exceed 512MB. Render will "kill" the process (OOM Error), and your site will crash.

### Railway (Free Trial / Hobby)
- **RAM Limit:** Railway is "usage-based." Their trial gives you a $5 credit.
- **Multi-Worker?** Technically, Railway is more flexible. If your app is small, you might fit **2 workers** within their trial resources, but you will use up your $5 credit faster.
- **Scaling:** Railway prefers "Horizontal Scaling"—instead of packing 4 chefs into one small kitchen, they prefer you open a second kitchen (a second "Service") if things get busy.

---

## 5. Why our recent fixes are "Pro" 🛡️
Because you are currently on a **Single Worker** (Render Free), race conditions are rare. However, the fixes we just applied (Atomic `F()` expressions, `Greatest()` floor, and Session Timestamps) are **Pro-Level** because:

1. They make your site **safe** for when you eventually move to 4 or 5 workers.
2. They protect your data integrity even if the network is laggy.
3. Your code is now "Scale-Ready"—you can upgrade your server tomorrow, and your code won't break!

---

**Summary:** Stay on **1 worker** while using Render's Free tier. If you ever upgrade or move to a paid plan on Railway/Render, increase to **2 or 3 workers** using the `-w` flag.
