import os
import re
import sqlite3
import fitz  # PyMuPDF
from docx import Document
from config import DB_PATH

CV_FOLDER = "data/CVs1"  

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text.strip()

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text.strip()

def get_candidate_name(filename):
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").replace("-", " ").title()

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def process_cvs():
    if not os.path.exists(CV_FOLDER):
        print(f"CV folder not found: {CV_FOLDER}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure email column exists
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'email' not in columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN email TEXT")

    files = os.listdir(CV_FOLDER)
    print(f"Found {len(files)} files in '{CV_FOLDER}'")

    for file in files:
        file_path = os.path.join(CV_FOLDER, file)
        if not os.path.isfile(file_path):
            continue

        ext = file.lower().split(".")[-1]
        if ext not in ["pdf", "docx"]:
            print(f"Skipping unsupported file: {file}")
            continue

        if ext == "pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == "docx":
            text = extract_text_from_docx(file_path)

        if not text:
            print(f"No text extracted from {file}, skipping...")
            continue

        candidate_name = get_candidate_name(file)
        email = extract_email(text)

        if not email:
            print(f"No email found in {candidate_name}'s CV. Skipping.")
            continue

        try:
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE email = ?", (email,))
            if cursor.fetchone()[0] > 0:
                print(f"Candidate '{candidate_name}' with email '{email}' already exists. Skipping.")
                continue

            cursor.execute(
                "INSERT INTO candidates (name, email, cv_text) VALUES (?, ?, ?)",
                (candidate_name, email, text)
            )
            print(f"Inserted: {candidate_name} ({email})")

        except Exception as e:
            print(f"Error inserting candidate '{candidate_name}': {e}")
            continue

    conn.commit()
    conn.close()
    print("CV processing complete.")

if __name__ == "__main__":
    process_cvs()
