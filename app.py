"""Job Fit Agent — Gradio app for Hugging Face Spaces.

Paste a job posting URL (or its text directly), provide your CV (paste or
upload a PDF/text file), and get an honest AI-generated fit analysis:
score, matching skills, gaps, and what to highlight in your application.

Run locally with:
    python app.py

Deploy on Hugging Face Spaces by uploading this repo and setting the
GEMINI_API_KEY secret in the Space settings.
"""

from __future__ import annotations

import io

import gradio as gr
from pypdf import PdfReader

from agent_core import analyze_fit
from agent_core import fetch_job_posting_text


def extract_text_from_file(file_path: str) -> str:
  """Extracts text from an uploaded CV file (PDF or plain text)."""
  if file_path is None:
    return ""

  if file_path.lower().endswith(".pdf"):
    try:
      reader = PdfReader(file_path)
      text = "\n".join(page.extract_text() or "" for page in reader.pages)
      return text.strip()
    except Exception as exc:  # noqa: BLE001
      return f"ERROR: Could not read PDF: {exc}"
  else:
    try:
      with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()
    except Exception as exc:  # noqa: BLE001
      return f"ERROR: Could not read file: {exc}"


def run_analysis(
    job_input_mode: str,
    job_url: str,
    job_text: str,
    cv_input_mode: str,
    cv_text: str,
    cv_file: str,
) -> str:
  """Orchestrates fetching/reading inputs and running the fit analysis."""

  # --- Resolve job posting text ---
  if job_input_mode == "URL":
    if not job_url or not job_url.strip():
      return "## Error\n\nPlease enter a job posting URL."
    posting_text = fetch_job_posting_text(job_url.strip())
  else:
    if not job_text or not job_text.strip():
      return "## Error\n\nPlease paste the job posting text."
    posting_text = job_text.strip()

  # --- Resolve candidate profile text ---
  if cv_input_mode == "Paste text":
    if not cv_text or not cv_text.strip():
      return "## Error\n\nPlease paste your CV text."
    profile_text = cv_text.strip()
  else:
    if not cv_file:
      return "## Error\n\nPlease upload your CV file (PDF or .txt)."
    profile_text = extract_text_from_file(cv_file)
    if profile_text.startswith("ERROR:"):
      return f"## Error\n\n{profile_text}"

  return analyze_fit(posting_text, profile_text)


def toggle_job_inputs(mode: str):
  return (
      gr.update(visible=(mode == "URL")),
      gr.update(visible=(mode == "Paste text")),
  )


def toggle_cv_inputs(mode: str):
  return (
      gr.update(visible=(mode == "Paste text")),
      gr.update(visible=(mode == "Upload file")),
  )


with gr.Blocks(
    title="Job Fit Agent",
) as demo:
  gr.Markdown(
      """
      # 🎯 Job Fit Agent

      An AI agent that compares a job posting against your CV and gives you
      an honest fit score, plus advice on what to highlight in your
      application. Built with the Groq API (Llama 3.3 70B).

      *Built while job hunting for AI Engineer roles in Germany —
      [read more on GitHub](https://github.com/negso98/job-fit-agent).*
      """
  )

  with gr.Row():
    with gr.Column():
      gr.Markdown("### 1. Job Posting")
      job_input_mode = gr.Radio(
          choices=["URL", "Paste text"],
          value="URL",
          label="How would you like to provide the job posting?",
      )
      job_url = gr.Textbox(
          label="Job posting URL",
          placeholder="https://www.linkedin.com/jobs/view/...",
          visible=True,
      )
      job_text = gr.Textbox(
          label="Job posting text",
          placeholder="Paste the full job description here...",
          lines=8,
          visible=False,
      )

      gr.Markdown("### 2. Your CV / Profile")
      cv_input_mode = gr.Radio(
          choices=["Paste text", "Upload file"],
          value="Paste text",
          label="How would you like to provide your CV?",
      )
      cv_text = gr.Textbox(
          label="Your CV / profile summary",
          placeholder=(
              "Paste a summary of your skills, work experience, projects, "
              "and education..."
          ),
          lines=10,
          visible=True,
      )
      cv_file = gr.File(
          label="Upload your CV (PDF or .txt)",
          file_types=[".pdf", ".txt"],
          visible=False,
      )

      analyze_btn = gr.Button("Analyze Fit 🔍", variant="primary")

    with gr.Column():
      gr.Markdown("### Result")
      output = gr.Markdown(
          label="Fit Analysis",
          value="*Your fit report will appear here once you run the analysis.*",
      )

  job_input_mode.change(
      toggle_job_inputs,
      inputs=job_input_mode,
      outputs=[job_url, job_text],
  )
  cv_input_mode.change(
      toggle_cv_inputs,
      inputs=cv_input_mode,
      outputs=[cv_text, cv_file],
  )

  analyze_btn.click(
      run_analysis,
      inputs=[job_input_mode, job_url, job_text, cv_input_mode, cv_text, cv_file],
      outputs=output,
  )

  gr.Markdown(
      """
      ---
      ⚠️ Your CV and the job posting text are sent to the Gemini API for
      analysis and are not stored anywhere by this app.
      """
  )


if __name__ == "__main__":
  demo.launch(theme=gr.themes.Soft(primary_hue="blue"))