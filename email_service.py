"""
Email delivery service for sending Anupamaa episode summaries to Navinram022@gmail.com.
Supports Gmail SMTP with App Passwords, with HTML fallback saving.
"""

import os
import json
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import BASE_DIR, TARGET_EMAIL

logger = logging.getLogger("AnupamaaBot.Email")
CONFIG_FILE = os.path.join(BASE_DIR, "email_config.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_email_config() -> dict:
    default_cfg = {
        "sender_email": "",
        "app_password": "",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "target_email": TARGET_EMAIL
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_cfg.update(cfg)
        except Exception as e:
            logger.warning(f"Error reading email_config.json: {e}")
    return default_cfg

def save_report_locally(title: str, date_str: str, gemini_result: str, link: str) -> str:
    """Saves report locally to an HTML file."""
    safe_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"Anupamaa_{safe_date}.html"
    report_path = os.path.join(REPORTS_DIR, file_name)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; line-height: 1.6; }}
        .card {{ max-width: 750px; margin: auto; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
        .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; }}
        h1 {{ color: #b91c1c; font-size: 24px; margin: 0 0 8px 0; }}
        .meta {{ font-size: 13px; color: #64748b; }}
        .badge {{ background: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
        .content {{ white-space: pre-wrap; font-size: 15px; color: #1e293b; background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #b91c1c; }}
        .footer {{ margin-top: 25px; font-size: 12px; color: #94a3b8; text-align: center; }}
        a {{ color: #2563eb; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <span class="badge">ANUPAMAA WRITTEN UPDATE</span>
            <h1>{title}</h1>
            <div class="meta">Date: {date_str} | <a href="{link}" target="_blank">Original JustShowBiz Source</a></div>
        </div>
        <div class="content">
{gemini_result}
        </div>
        <div class="footer">
            Generated automatically by Anupamaa AutoBot & Gemini
        </div>
    </div>
</body>
</html>
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    logger.info(f"Report saved locally to: {report_path}")
    return report_path

def send_email_report(title: str, date_str: str, gemini_result: str, link: str) -> bool:
    """
    Sends the Gemini result as an email to TARGET_EMAIL.
    Also saves a local copy under reports/.
    """
    local_file = save_report_locally(title, date_str, gemini_result, link)
    cfg = load_email_config()
    sender = cfg.get("sender_email", "").strip()
    password = cfg.get("app_password", "").strip()
    target = cfg.get("target_email", TARGET_EMAIL).strip()
    
    if not sender or not password:
        logger.warning(
            f"Email sender credentials not yet provided in 'email_config.json'. "
            f"The report has been saved locally at: {local_file}. "
            f"To enable direct email sending to {target}, please set sender_email and app_password."
        )
        return False
        
    logger.info(f"Sending email from {sender} to {target} via {cfg['smtp_server']}...")
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📺 Anupamaa Episode Update - {date_str}"
    msg["From"] = f"Anupamaa Bot <{sender}>"
    msg["To"] = target
    
    # Plain text version
    plain_text = f"{title}\nDate: {date_str}\nSource: {link}\n\n--- GEMINI RESULT ---\n\n{gemini_result}"
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    
    # HTML version
    with open(local_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        server = smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"], timeout=30)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [target], msg.as_string())
        server.quit()
        logger.info(f"Email successfully delivered to {target}!")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {e}")
        return False
