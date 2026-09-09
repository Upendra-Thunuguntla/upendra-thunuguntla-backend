import os
import json
import base64
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        self._send_json_response(200, {
            "status": "healthy",
            "service": "Upendra Thunuguntla Resume Serverless API (Python)",
            "endpoint": "/api/send-resume"
        })

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
            
            try:
                payload = json.loads(body_bytes.decode('utf-8'))
            except Exception:
                payload = {}

            email = payload.get('email', '').strip()
            name = payload.get('name', '').strip()
            company = payload.get('company', '').strip()
            source_page = payload.get('source_page', 'https://upendra.fyi')
            timestamp = payload.get('timestamp', '')

            # Basic Validation
            if not email or '@' not in email or '.' not in email:
                self._send_json_response(400, {'error': 'Please provide a valid email address.'})
                return

            api_key = os.environ.get('RESEND_API_KEY')
            if not api_key:
                print('[SendResume] Missing RESEND_API_KEY environment variable.')
                self._send_json_response(500, {
                    'error': 'Backend email service is pending setup. RESEND_API_KEY environment variable is missing.'
                })
                return

            from_email = os.environ.get('FROM_EMAIL', 'Upendra Thunuguntla <onboarding@resend.dev>')
            cc_email = os.environ.get('CC_EMAIL', 'upendra.thunuguntla@gmail.com')
            resume_url = os.environ.get(
                'GOOGLE_DOCS_RESUME_URL',
                'https://docs.google.com/document/d/1lFxZsurq577mSmrpP7myvaFWSUFi6Ylh4sSRh4KOZbg/export?format=pdf'
            )

            # 1. Fetch Resume PDF from Google Docs
            attachments = []
            try:
                req = urllib.request.Request(
                    resume_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) UpendraResumeBot/1.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        pdf_bytes = resp.read()
                        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        attachments.append({
                            'filename': 'Upendra_Thunuguntla_Resume.pdf',
                            'content': b64_pdf
                        })
            except Exception as pdf_err:
                print(f"[SendResume] Warning fetching PDF from Google Docs: {pdf_err}")

            # 2. Send email to visitor (with CC to Upendra) via Resend API
            visitor_html = get_visitor_email_html(name, resume_url)
            visitor_payload = {
                'from': from_email,
                'to': [email],
                'subject': 'Upendra Thunuguntla — Resume & Enterprise Integration Portfolio',
                'html': visitor_html
            }

            if cc_email:
                visitor_payload['cc'] = [cc_email]

            if attachments:
                visitor_payload['attachments'] = attachments

            resend_result, status_code = send_resend_email(api_key, visitor_payload)

            if status_code not in (200, 201):
                err_msg = 'Failed to send resume email.'
                if isinstance(resend_result, dict):
                    err_msg = resend_result.get('message', resend_result.get('name', err_msg))
                self._send_json_response(400, {'error': err_msg})
                return

            self._send_json_response(200, {
                'success': True,
                'message': 'Resume dispatched successfully! Please check your email inbox.'
            })

        except Exception as e:
            print(f"[SendResume] Internal Error: {e}")
            self._send_json_response(500, {'error': 'Internal server error processing request.'})

    def _send_json_response(self, status_code, body):
        self.send_response(status_code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))


def send_resend_email(api_key, payload):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "UpendraResumeBackendPython/1.0"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            resp_bytes = resp.read()
            resp_json = json.loads(resp_bytes.decode('utf-8')) if resp_bytes else {}
            return resp_json, resp.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = {'message': err_body}
        return err_json, e.code
    except Exception as e:
        return {'message': str(e)}, 500


def get_visitor_email_html(name, resume_url):
    greeting = f"Hi {escape_html(name)}," if name else "Hi there,"
    safe_resume_url = escape_html(resume_url)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Upendra Thunuguntla — Resume</title>
</head>
<body style="margin:0; padding:0; background-color:#0f172a; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#e2e8f0;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#0f172a; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="600" border="0" cellspacing="0" cellpadding="0" style="max-width:600px; width:100%; background-color:#1e293b; border-radius:12px; border:1px solid #334155; overflow:hidden;">
          
          <!-- Header Bar -->
          <tr>
            <td style="background: linear-gradient(135deg, #0284c7 0%, #3b82f6 100%); padding: 28px 32px; text-align: left;">
              <h1 style="margin:0; font-size:22px; color:#ffffff; font-weight:700; letter-spacing:-0.5px;">
                Upendra Thunuguntla
              </h1>
              <p style="margin:4px 0 0 0; font-size:14px; color:#e0f2fe;">
                Senior MuleSoft & Enterprise Integration Architect
              </p>
            </td>
          </tr>

          <!-- Main Content -->
          <tr>
            <td style="padding: 32px; font-size:15px; line-height:1.6; color:#cbd5e1;">
              <p style="margin-top:0; font-size:16px; color:#f8fafc; font-weight:600;">
                {greeting}
              </p>
              
              <p style="margin-bottom:20px;">
                Thank you for your interest in my background! As requested, I have attached my latest <strong>PDF Resume</strong> to this email.
              </p>

              <div style="background-color:#0f172a; border-left:4px solid #3b82f6; border-radius:4px; padding:16px 20px; margin:24px 0;">
                <p style="margin:0 0 8px 0; font-weight:600; color:#f8fafc; font-size:14px;">⚡ Core Specializations:</p>
                <ul style="margin:0; padding-left:20px; color:#94a3b8; font-size:14px;">
                  <li>MuleSoft Anypoint Platform (CloudHub 2.0, RTF, On-Prem)</li>
                  <li>REST / SOAP / GraphQL API Architecture & RAML / OpenAPI Spec Design</li>
                  <li>DataWeave 2.0 Complex Transformations & Enterprise Integration Patterns</li>
                  <li>CI/CD Automation, Custom Connectors, Mule 3 to Mule 4 Migrations</li>
                </ul>
              </div>

              <!-- CTA Buttons -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 28px 0 16px 0;">
                <tr>
                  <td align="center">
                    <a href="https://upendra.fyi" target="_blank" style="display:inline-block; background-color:#3b82f6; color:#ffffff; font-weight:600; font-size:14px; padding:12px 28px; border-radius:8px; text-decoration:none; margin-right:12px;">
                      🌐 Visit Interactive Portfolio
                    </a>
                    <a href="{safe_resume_url}" target="_blank" style="display:inline-block; background-color:#334155; color:#e2e8f0; font-weight:600; font-size:14px; padding:12px 24px; border-radius:8px; text-decoration:none; border:1px solid #475569;">
                      📄 Direct PDF Link
                    </a>
                  </td>
                </tr>
              </table>

              <hr style="border:0; border-top:1px solid #334155; margin: 28px 0;" />

              <p style="margin:0; font-size:14px; color:#94a3b8;">
                Feel free to reply directly to this email or connect with me on 
                <a href="https://www.linkedin.com/in/upendra-thunuguntla/" target="_blank" style="color:#60a5fa; text-decoration:underline;">LinkedIn</a>.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#0f172a; padding: 20px 32px; text-align: center; font-size:12px; color:#64748b; border-top:1px solid #1e293b;">
              © Upendra Thunuguntla • <a href="https://upendra.fyi" style="color:#64748b; text-decoration:none;">upendra.fyi</a>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_notification_email_html(data):
  email = escape_html(data.get('email', ''))
  name = escape_html(data.get('name', 'Not provided'))
  company = escape_html(data.get('company', 'Not provided'))
  source_page = escape_html(data.get('sourcePage', 'https://upendra.fyi'))
  timestamp = escape_html(data.get('timestamp', ''))
  ip = escape_html(data.get('ip', 'Unknown'))

  return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>New Resume Lead</title></head>
<body style="font-family: Arial, sans-serif; background:#f1f5f9; padding: 20px; color:#334155;">
  <div style="max-width: 550px; margin: 0 auto; background: #ffffff; border-radius: 8px; border:1px solid #e2e8f0; padding: 24px;">
    <h2 style="margin-top:0; color:#0f172a; font-size:18px;">📄 New Resume Request Captured</h2>
    <p style="font-size:14px; color:#64748b;">Someone just requested your resume on <strong>upendra.fyi</strong>!</p>
    
    <table width="100%" border="0" cellspacing="0" cellpadding="8" style="font-size:14px; border-collapse: collapse; margin-top:16px;">
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td width="30%" style="font-weight:bold; color:#475569;">Email:</td>
        <td style="color:#0284c7; font-weight:bold;">{email}</td>
      </tr>
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="font-weight:bold; color:#475569;">Name:</td>
        <td>{name or 'Not provided'}</td>
      </tr>
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="font-weight:bold; color:#475569;">Company / Role:</td>
        <td>{company or 'Not provided'}</td>
      </tr>
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="font-weight:bold; color:#475569;">Timestamp:</td>
        <td>{timestamp}</td>
      </tr>
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="font-weight:bold; color:#475569;">Source Page:</td>
        <td><a href="{source_page}" target="_blank" style="color:#2563eb;">{source_page}</a></td>
      </tr>
      <tr>
        <td style="font-weight:bold; color:#475569;">Visitor IP:</td>
        <td style="font-family:monospace;">{ip}</td>
      </tr>
    </table>

    <div style="margin-top:24px; text-align:center;">
      <a href="mailto:{email}?subject=Following%20up%20from%20upendra.fyi" style="display:inline-block; background:#0284c7; color:#ffffff; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:13px;">
        ✉️ Reply to Lead
      </a>
    </div>
  </div>
</body>
</html>"""


def escape_html(text):
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )
