import sqlite3
import smtplib
import random
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import DB_PATH, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INTERVIEW_SLOTS = [
    "Monday, 10:00 AM",
    "Tuesday, 2:00 PM",
    "Wednesday, 11:30 AM",
    "Thursday, 4:00 PM",
    "Friday, 1:00 PM"
]

def generate_email(name, job_title, interview_slot):
    subject = f"Interview Invitation for {job_title}"
    body = f"""
Dear {name},

Congratulations! Based on your profile, you have been shortlisted for the role of <b>{job_title}</b>.

We would like to invite you for an interview on <b>{interview_slot}</b>. The interview will be conducted via Google Meet and will last approximately 45 minutes.

Please confirm your availability by replying to this email.

Best regards,<br>
<b>HR Team</b>
"""
    return subject, body

def send_email(recipient_email, subject, body):
    if not recipient_email:
        raise ValueError("Recipient email address is missing.")
    
    msg = MIMEMultipart("alternative")
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"SMTP send failed for {recipient_email}: {e}")

def ensure_email_sent_column(cursor):
    cursor.execute("PRAGMA table_info(shortlisted_candidates)")
    if 'email_sent' not in [col[1] for col in cursor.fetchall()]:
        cursor.execute("ALTER TABLE shortlisted_candidates ADD COLUMN email_sent INTEGER DEFAULT 0")

def schedule_interviews():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ensure_email_sent_column(cursor)

    cursor.execute("""
        SELECT sc.id, sc.name, sc.email, j.job_title
        FROM shortlisted_candidates sc
        JOIN jobs j ON sc.job_id = j.id
        WHERE sc.email_sent = 0
    """)
    candidates = cursor.fetchall()

    if not candidates:
        logging.info("All shortlisted candidates have already received interview emails.")
        conn.close()
        return

    for sc_id, name, email, job_title in candidates:
        logging.info(f"Preparing to send email to: {name} ({email}) for role: {job_title}")
        try:
            if not email:
                raise ValueError(f"Missing email for candidate ID {sc_id}")

            slot = random.choice(INTERVIEW_SLOTS)
            subject, body = generate_email(name, job_title, slot)
            send_email(email, subject, body)

            cursor.execute("UPDATE shortlisted_candidates SET email_sent = 1 WHERE id = ?", (sc_id,))
            logging.info(f" Email successfully sent to {email}")

        except Exception as e:
            logging.error(f"Failed to send interview email to {name} ({email}): {e}")

    conn.commit()
    conn.close()
    logging.info("Email job completed and database updated.")

if __name__ == "__main__":
    schedule_interviews()
