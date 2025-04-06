# SmartHireX: AI-Enhanced Recruitment with Matchmaking & Interview Automation


**SmartHireX** is an AI-powered, agent-based hiring automation platform. It leverages large language models (Llama3.1) and vector-based similarity scoring to streamline resume parsing, candidate-job matching, and automated interview scheduling. The system is modular, extensible, and optimized for local LLMs such as LLaMA 3.1 via Ollama.

---

## Features

- Agent-based design: modular, functional units (JD Summarizer, CV Extractor, Matching Agent, etc.)
- LLM-driven information extraction from resumes and job descriptions
- Semantic job-candidate matching using vector embeddings
- Automated candidate shortlisting with threshold control
- One-click interview scheduling with email integration
- SQLite3-powered backend for lightweight deployments

---

## Technologies Used

- **LLM**: LLaMA 3.1 via Ollama (`ollama.chat`, `ollama.embeddings`)
- **Database**: SQLite3
- **Email**: Python `smtplib`
- **Matching**: Cosine similarity on dense embeddings
- **File Handling**: `PyMuPDF` for PDF extraction

---

## Installation

```bash
pip install -r requirements.txt
```

---

## SmartHireX Agents & Execution Flow

```bash
# Step 1: DATABASE INITIALIZATION
python database_setup.py

# Step 2: JD SUMMARIZING AGENT
# → Uses Llama3.1 model to extract required qualifications from job descriptions
python jd_summarizer.py

# Step 3: JOB LOADER
# → Loads summarized job descriptions into the jobs table
python load_jobs.py

# Step 4: CV EXTRACTOR AGENT
# → Parses resumes from uploaded PDFs and extracts structured data 
python process_cvs.py

# Step 5: MATCHING AGENT
# → Matches candidates to job descriptions using cosine similarity on embeddings
python match_candidates.py

# Step 6: SHORTLISTING AGENT
# → Filters candidates based on threshold and stores them in a shortlist table
python shortlist_candidates.py

# Step 7: INTERVIEW SCHEDULER AGENT
# → Randomly schedules interviews and sends emails to shortlisted candidates
python interview_scheduler.py
```

---

## Configuration (`config.py`)

```python
# File: config.py
DB_PATH = "database/smarthirex.db"
OLLAMA_MODEL = "llama3.1"

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@example.com"
SMTP_PASSWORD = "your_app_password"
```

---

## Database Design

- **candidates**
  - `id`, `name`, `email`, `skills`, `experience`, `match_score`, `matched_job_id`

- **jobs**
  - `id`, `job_title`, `job_description`, `summarized_qualifications`

- **shortlisted_candidates**
  - `candidate_id`, `job_id`, `match_score`, `email_sent`

Refer to `database_setup.py` for schema details.

---

## Matching Algorithm

- Resumes and job qualifications are vectorized via `ollama.embeddings()`
- Cosine similarity is used to compute match scores between candidates and roles
- Only candidates above a configurable threshold (default = 70%) are shortlisted

---

## Interview Scheduling

- Predefined time slots are randomly assigned
- Emails are generated with role-based templates and sent via SMTP
- Status is recorded in the database to avoid resending

---

## License

This project is licensed under the MIT License.

---

## Authors

Developed by Team "TalentSage" for the "Accenture Data and AI Hackathon - Hack the Future: A Gen AI Sprint Powered by Data"

