# Document Plagiarism Checker

A web application that checks whether a piece of text was copied from the internet or from previously checked documents, using **text similarity matching**. Paste your text into a single box (or upload a file) and the system searches Wikipedia and DuckDuckGo, compares the results, and tells you how much of your text appears elsewhere and where it came from.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-web%20framework-1550e6)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![Status](https://img.shields.io/badge/Status-Academic%20project-lightgrey)

---

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Usage](#usage)
7. [Testing the System](#testing-the-system)
8. [Deployment (Render)](#deployment-render)
9. [Configuration](#configuration)
10. [Limitations](#limitations)
11. [Future Improvements](#future-improvements)
12. [Troubleshooting](#troubleshooting)
13. [Author](#author)

---

## Features

- **Single input box.** Paste text or upload a `.pdf`, `.docx` or `.txt` file.
- **Automatic internet search** on Wikipedia and DuckDuckGo, no manual searching needed.
- **Local database check.** Every checked text is saved, so later submissions are also compared against earlier ones.
- **Clear result:** overall similarity percentage, a verdict, and a table of matching sources with clickable links.
- **Highlighted text.** The parts of your text that were found elsewhere are marked in blue.
- **Export.** Download a PDF report (via the browser's print dialog) or a plain-text report.
- **Clean, responsive interface** in blue and white, with small animations and a custom favicon.

## How It Works

1. **Input and cleaning.** The text is read (from the box or an uploaded file), and citation markers such as `[1]` or `[A]` are removed.
2. **Shingling.** The text is split into overlapping groups of **4 consecutive words** (4-grams).
3. **Search.** Up to **5 prose sentences** are selected. Each one is searched on Wikipedia (official API) and DuckDuckGo.
4. **Fetching.** Up to **10 result pages** are downloaded in parallel and their text is extracted.
5. **Matching.** The 4-grams of your text are compared with every page and with every document stored in the database.
6. **Scoring.** The overall percentage is the share of your 4-grams found in at least one source. A per-source percentage is also shown.
7. **Verdict.**

| Similarity | Verdict |
|---|---|
| Below 15% | Original text: no copied content found |
| 15% to 40% | Some parts may have been copied |
| 40% and above | Plagiarized: copied content found |

8. **Saving.** The checked text is stored in SQLite for future comparisons.

The repository also contains classic similarity measures (**TF-IDF with cosine similarity** and **Jaccard similarity**) in `similarity.py`, together with text preprocessing (tokenization, stop-word removal and stemming) in `preprocess.py`.

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Flask, Jinja2 templates |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Similarity and NLP | scikit-learn (TF-IDF, cosine), NLTK (stop words, stemming) |
| File reading | pypdf (PDF), python-docx (Word) |
| Web access | requests, BeautifulSoup4, ddgs (DuckDuckGo) |
| Production server | gunicorn |
| Hosting | Render |

## Project Structure

```
plagiarism-checker/
├── app.py              # Flask routes and SQLite database functions
├── webcheck.py         # Internet search, page fetching, scoring, verdict
├── similarity.py       # N-grams, TF-IDF cosine, Jaccard, highlighting
├── preprocess.py       # Tokenization, stop words, stemming
├── extract.py          # Text extraction from PDF, DOCX and TXT
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Single-page user interface
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.12 or 3.13** (very new versions such as 3.15 may not be supported by every library yet)
- **pip** (included with Python)
- An internet connection (needed for searching)

### Installation

1. **Download the project.** Clone the repository or download it as a ZIP file and extract it.

   ```bash
   git clone https://github.com/<your-username>/plagiarism-checker.git
   cd plagiarism-checker
   ```

   If you downloaded a ZIP, open the extracted folder that directly contains `app.py`.

2. **Create a virtual environment (recommended).**

   Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   macOS / Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies.**

   ```bash
   python -m pip install -r requirements.txt
   ```

   If `ddgs` fails to install, you can ignore it. The app falls back to another DuckDuckGo method, and Wikipedia search works either way.

4. **Run the app.**

   ```bash
   python app.py
   ```

5. **Open it in your browser:** <http://127.0.0.1:5000>

On the first run, NLTK downloads its English stop-word list automatically, so keep your internet connection on.

## Usage

1. Paste your text into the box, or choose a `.pdf`, `.docx` or `.txt` file. At least **8 words** are required.
2. Click **Check plagiarism** and wait up to about 30 seconds while the internet is searched.
3. Read the result:
   - the **percentage** and **verdict**
   - the number of **web pages checked**
   - the **matching sources** table, with links
   - your text, with matched parts highlighted in blue
4. Use **Download PDF report** (choose *Save as PDF* in the print window) or **Download text report (.txt)** to keep the result.
5. **Clear database** removes all saved documents. Use it when you want to re-test the same text, because a saved text will otherwise match itself.

## Testing the System

| Test | Input | Expected result |
|---|---|---|
| Copied text | Three or four prose sentences copied from a Wikipedia article | 40% or higher, with a link to Wikipedia |
| Partly copied | Two copied sentences plus two sentences you wrote yourself | Roughly 15% to 60% |
| Original text | Several sentences you wrote yourself | Close to 0% |

Tip: copy normal paragraph text, not tables or info boxes, which are too short and fragmented to match reliably.

## Deployment (Render)

1. Push the project to a GitHub repository. Do not upload `venv/`, `__pycache__/` or `history.db`.
2. Make sure `requirements.txt` contains `gunicorn`.
3. In `app.py`, call `init_db()` on its own line above `if __name__ == "__main__":` so the database table is created when running under gunicorn.
4. On [render.com](https://render.com), create a **New Web Service** from the repository and use:

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |
| Environment variable | `PYTHON_VERSION` = `3.12.7` |

5. Render redeploys automatically whenever you commit to the repository.

Notes for the free plan: the service sleeps after a period of inactivity and takes about a minute to wake up, and the SQLite file may be reset when the service restarts.

## Configuration

Key settings are at the top of `webcheck.py`:

| Setting | Default | Meaning |
|---|---|---|
| `N` | `4` | Words per shingle (n-gram size) |
| `MAX_QUERIES` | `5` | Number of sentences searched online |
| `MAX_PAGES` | `10` | Maximum pages downloaded per check |

The verdict thresholds (15% and 40%) are defined in the `verdict()` function of `webcheck.py`.

## Limitations

- Detects **copied wording** only. It cannot recognize paraphrasing or translation.
- Results depend on what the search engines return, and search may occasionally be blocked or rate-limited.
- Only **public web pages** can be read. Paywalled, login-protected or scanned (image-only) content is not checked.
- The similarity percentage is an indicator, not proof of plagiarism. Properly quoted and cited text can also match, so the final judgment belongs to a human reviewer.
- Saved texts are stored in the database without the author's identity. Do not submit confidential documents to a shared deployment.

## Future Improvements

- Semantic similarity with language models (for example BERT embeddings) to catch paraphrasing
- Additional search sources (Google Programmable Search, academic databases)
- Support for more languages, including Somali and Arabic
- User accounts, private history and an option not to store submitted text
- Rate limiting and upload size limits for production use
- Server-generated PDF reports

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python and tick **Add python.exe to PATH**, then reopen the terminal |
| `No module named flask` | Activate the virtual environment and run `python -m pip install -r requirements.txt` |
| `TemplateNotFound: index.html` | The file must be at `templates/index.html` (check the exact name and folder) |
| Page shows an old design or icon | Hard refresh with Ctrl + F5, or open a private window |
| "No results were found on the internet" | Check your connection and try again. Search engines can occasionally block requests |
| Text matches itself | It was saved earlier. Click **Clear database** |
| Render deploy fails | Open the deploy **Logs**, and check `PYTHON_VERSION`, `requirements.txt` and the Start Command |

## Author

**Amiin Abdalla**
Developed as a university project: *Document Plagiarism Checker using Text Similarity Matching*.

> This project was built for academic purposes. Add a license file (for example MIT) before reusing or redistributing it.
