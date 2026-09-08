"""Core agent logic for the Job Fit Agent.

This module wraps a Google ADK agent that:
1. Fetches a job posting from a URL (or accepts pasted text directly)
2. Compares it against a candidate's CV/profile (provided by the user,
   not hardcoded)
3. Returns a structured fit analysis: score, matching skills, gaps, and
   advice on what to highlight in the application

Kept separate from the UI layer (app.py) so the agent logic can be reused
or tested independently of Gradio.
"""

from __future__ import annotations

import os

import requests
from bs4 import BeautifulSoup
from groq import Groq


MODEL_NAME = "qwen/qwen3.6-27b"


def fetch_job_posting_text(url: str) -> str:
  """Fetches a job posting page from a URL and returns its clean visible text.

  Args:
    url: The URL of the job posting to fetch.

  Returns:
    The extracted, cleaned text content of the page (truncated to a
    reasonable length), or a string starting with 'ERROR:' if the fetch
    failed.
  """
  try:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; JobFitAgent/1.0)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
      tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return clean_text[:8000]
  except Exception as exc:  # noqa: BLE001
    return f"ERROR: Could not fetch job posting from {url}: {exc}"


SYSTEM_INSTRUCTION = """You are an honest, supportive career advisor helping a candidate evaluate a job posting against their own CV/profile.

You will be given:
1. JOB POSTING TEXT (extracted from a URL or pasted by the user)
2. CANDIDATE PROFILE (their CV, pasted or extracted from an uploaded file)

Analyze the job posting and extract: job title, company, required skills,
nice-to-have skills, experience level, and key responsibilities.

Then compare it against the candidate profile and produce a structured
markdown report with these exact sections:

## Job Fit Report

**Role:** <job title> at <company>
**Experience level required:** <level>

### Fit Score: <X>/100

Be realistic and honest here. Do not just count keyword overlaps — weigh
genuine relevant experience, transferable skills, and depth of experience
more heavily than surface-level keyword matching.

### ✅ Matching Skills
- bullet list of skills/experience the candidate has that directly match

### ⚠️ Gaps
- bullet list of required or nice-to-have skills the candidate doesn't
  clearly have

### 💡 What to Highlight
- specific, actionable advice on what to emphasize in the application or
  CV for this particular role

### Summary
A 2-3 sentence honest take on whether the candidate should apply and why.

Be balanced — not overly optimistic, not overly harsh. If the job posting
text looks empty, broken, or like an error message, say so clearly and ask
the user to paste the job description text manually instead.
"""


def analyze_fit(job_posting_text: str, candidate_profile: str) -> str:
  """Runs the fit analysis using Gemini directly (no ADK dependency).

  Args:
    job_posting_text: The job posting content (from URL fetch or pasted).
    candidate_profile: The candidate's CV/profile text.

  Returns:
    A markdown-formatted fit report.
  """
  api_key = os.environ.get("GROQ_API_KEY")
  if not api_key:
    return (
        "## Error\n\nNo `GROQ_API_KEY` found in environment. Please set "
        "it as a secret in your Hugging Face Space settings, or as an "
        "environment variable if running locally. Get a free key at "
        "https://console.groq.com/keys"
    )

  if not job_posting_text or job_posting_text.startswith("ERROR:"):
    return (
        f"## Error\n\nCouldn't read the job posting.\n\n```\n"
        f"{job_posting_text}\n```\n\nTry pasting the job description text "
        f"directly instead of a URL."
    )

  if not candidate_profile or not candidate_profile.strip():
    return (
        "## Error\n\nNo candidate profile provided. Please paste your CV "
        "text or upload a CV file before running the analysis."
    )

  client = Groq(api_key=api_key)

  user_prompt = (
      f"JOB POSTING TEXT:\n{job_posting_text}\n\n"
      f"CANDIDATE PROFILE:\n{candidate_profile}\n"
  )

  response = client.chat.completions.create(
      model=MODEL_NAME,
      messages=[
          {"role": "system", "content": SYSTEM_INSTRUCTION},
          {"role": "user", "content": user_prompt},
      ],
      temperature=0.4,
  )

  return response.choices[0].message.content
