# Upendra Thunuguntla — Backend API (Vercel Python Serverless)

Vercel Python Serverless API for **Resume Delivery & Lead Capture** on `upendra.fyi`.

## 🚀 Features

- **Serverless API**: Python 3 runtime hosted on Vercel Serverless Functions (`/api/send-resume`).
- **Dynamic Attachment**: Fetches the latest Resume PDF from Google Docs and attaches it to the email.
- **Resend Email Integration**: Dispatches HTML email with PDF attachment to the requester while CCing `upendra.thunuguntla@gmail.com`.
- **CORS Enabled**: Configured for cross-origin access from `upendra.fyi`, `api.upendra.fyi`, `backend.upendra.fyi`, and GitHub Pages.

---

## 📂 Repository Structure

```
.
├── api/
│   └── send-resume.py   # Main Python Serverless Function (Vercel HTTP handler)
├── vercel.json          # Vercel route & CORS configuration
├── requirements.txt     # Python runtime dependencies
├── .env.example         # Required Environment Variables template
└── README.md            # Backend documentation
```

---

## ⚙️ Environment Variables Setup

Configure these environment variables in your **Vercel Dashboard > Project Settings > Environment Variables**:

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `RESEND_API_KEY` | **Yes** | — | API Key from [Resend.com](https://resend.com) |
| `FROM_EMAIL` | Optional | `Upendra Thunuguntla <onboarding@resend.dev>` | Verified sender address |
| `CC_EMAIL` | Optional | `upendra.thunuguntla@gmail.com` | CC address for receiving lead copies |
| `GOOGLE_DOCS_RESUME_URL` | Optional | Google Docs export link | Target Google Docs PDF export URL |

---
