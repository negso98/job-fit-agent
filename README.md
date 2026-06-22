---
title: Job Fit Agent
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# Job Fit Agent 🎯

An AI agent that compares a job posting against your CV/profile and gives
you an honest, structured fit analysis: a fit score, matching skills,
gaps, and concrete advice on what to highlight in your application.

**[Try the live demo on Hugging Face Spaces →](https://huggingface.co/spaces/negso98/job-fit-agent)**

## Why I built this

I built this while actively job hunting for AI Engineer roles in Germany.
Instead of manually re-reading every job posting and guessing how well I
matched, I wanted a tool that could do that comparison for me and tell me
honestly where I stood — and what to emphasize when I applied.

## How it works

1. **Input the job posting** — either paste a URL (the app fetches and
   extracts the visible text) or paste the job description directly.
2. **Input your CV** — paste your CV text or upload a PDF/text file.
3. **Gemini analyzes both** and returns a structured markdown report:
   - Fit score (0-100), weighted toward genuine relevant experience, not
     just keyword overlap
   - Matching skills
   - Gaps
   - What to highlight in your application
   - An honest summary

```
[URL fetch / pasted text] ─┐
                            ├─→ Gemini (system instruction + both inputs) ─→ Markdown report
[CV paste / PDF upload]   ─┘
```

## Tech stack

- **Gradio** — web UI, deployed on Hugging Face Spaces
- **Groq API** (Llama 3.3 70B) — analysis and report generation, free tier
- **BeautifulSoup + Requests** — job posting web scraping
- **pypdf** — CV PDF text extraction

## Running locally

1. Clone this repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a free Groq API key from
   [console.groq.com/keys](https://console.groq.com/keys) and set it
   as an environment variable:

   **Windows (CMD):**
   ```bash
   set GROQ_API_KEY=your_api_key_here
   ```
   **macOS/Linux:**
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open the local URL Gradio prints (usually `http://127.0.0.1:7860`).

## Deploying on Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space),
   choosing the **Gradio** SDK.
2. Upload `app.py`, `agent_core.py`, and `requirements.txt`.
3. In the Space settings, add a **secret** named `GROQ_API_KEY` with
   your Groq API key.
4. The Space will build and deploy automatically.

## What I learned

- Building a real, usable web UI for an AI tool with Gradio instead of a
  developer-only CLI/local server
- Designing flexible input handling (URL vs. pasted text, pasted CV vs.
  PDF upload) so the tool works for more real-world use cases
- Using a single well-structured system instruction to get consistent,
  structured markdown output from an LLM, without needing a rigid JSON
  schema
- Handling failure cases gracefully (broken URLs, empty inputs, missing
  API keys) so the app fails with a clear message instead of crashing

## Future improvements

- Support comparing one CV against multiple job postings and ranking them
- Add a downloadable PDF/markdown export of the fit report
- Cache repeated analyses to reduce API calls
