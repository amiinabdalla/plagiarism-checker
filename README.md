# Document Plagiarism Checker

A Flask web application that measures **text similarity** between documents and checks texts against the internet. It has two modes:

1. **Compare two documents.** Upload or paste two documents. The system computes their similarity using **TF-IDF and cosine similarity** and classifies the result as *High*, *Moderate* or *Low Similarity* using IF-THEN rules (70 / 40).
2. **Check against the internet** (additional feature). Paste one text, and the system searches Wikipedia and DuckDuckGo, compares the pages it finds with your text, and shows matching sources with the matching parts highlighted.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-web%20framework-1550e6)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![Tests](https://img.shields.io/badge/Tests-pytest-1550e6)
![Status](https://img.shields.io/badge/Status-Academic%20project-lightgrey)

> **Important.** This tool measures similarity. It does not decide whether plagiarism occurred. Quoted and properly cited text can also match, so a human reviewer must make the final judgment.

---

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Usage](#usage)
7. [Running the Tests](#running-the-tests)
8. [Deployment (Render)](#deployment-render)
9. [Configuration](#configuration)
10. [Security and Privacy](#security-and-privacy)
11. [Limitations](#limitations)
12. [Future Improvements](#future-improvements)
13. [Troubleshooting](#troubleshooting)
14. [Change Log](#change-log)
15. [Authors](#authors)

---

## Features

- **Two modes** in one interface, switched with tabs.
- **TF-IDF + cosine similarity** for comparing two documents, with Jaccard similarity and 4-word overlap shown as supporting measures.
- **IF-THEN classification:** 70% or higher is *High Similarity*, 40% to 69.9% is *Moderate Similarity*, below 40% is *Low Similarity*.
- **Internet check** on Wikipedia (official API) and DuckDuckGo, with a table of matching sources and clickable links.
- **Highlighting.** The parts of the text that match are marked in blue, so a reviewer can find them quickly.
- **File upload:** `.pdf`, `.docx` and `.txt`, up to 10 MB. Scanned PDFs without text produce a clear message.
- **Optional saving.** A text is stored in the database only if the user ticks *Save this text to the database*.
- **Export:** PDF report (through the browser print dialog) and plain-text report.
- **Responsive blue and white interface** with small animations and a custom favicon.
- **Automated tests** (pytest) for the similarity logic.

## How It Works

The processing follows five stages: **input, processing, representation, similarity, interpretation.**

### Mode 1: Compare two documents

1. **Input.** Two texts (typed or extracted from files). Citation markers such as `[1]` are removed.
2. **Processing.** Each text is converted to lowercase, tokenized, stripped of stop words (English and Somali) and stemmed (Porter stemmer).
3. **Representation.** The two texts are converted to **TF-IDF** vectors.
4. **Similarity.** **Cosine similarity** between the vectors gives a score from 0% to 100%. Jaccard similarity and the share of shared 4-word sequences are also reported.
5. **Interpretation.** The score is classified:

| Score | Result |
|---|---|
| 70% and above | High Similarity |
| 40% to 69.9% | Moderate Similarity |
| Below 40% | Low Similarity |

The 4-word sequences that appear in both documents are highlighted in both texts.

### Mode 2: Check against the internet

1. The text is split into overlapping groups of **4 consecutive words** (4-grams).
2. Up to **5 prose sentences** are selected (tables and info boxes are skipped) and searched on Wikipedia and DuckDuckGo.
3. Up to **10 result pages** are downloaded in parallel and their text is extracted.
4. The text's 4-grams are compared with every page, and with every document previously saved in the database.
5. The overall percentage is the share of the text's 4-grams found in at least one source. Each source also gets its own percentage.

| Share of text matched | Result |
|---|---|
| Below 15% | Low Similarity |
| 15% to 39.9% | Moderate Similarity |
| 40% and above | High Similarity |

> The percentages of the two modes are **different measures** and must not be compared directly. Cosine similarity compares the overall vocabulary of two documents and can score reworded text, while 4-gram matching finds only copied word sequences and scores reworded text close to 0%.

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Flask, Jinja2 |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Similarity and NLP | scikit-learn (TF-IDF, cosine, English stop words), NLTK (Porter stemmer) |
| File reading | pypdf (PDF), python-docx (Word) |
| Web access | requests, BeautifulSoup4, ddgs |
| Testing | pytest |
| Production server | gunicorn |
| Hosting | Render |

## Project Structure

```
plagiarism-checker/
├── app.py                   # Flask routes, SQLite database, the two modes
├── webcheck.py              # Internet search, page fetching, scoring, wording
├── similarity.py            # N-grams, TF-IDF cosine, Jaccard, classify(), highlighting
├── preprocess.py            # Tokenization, stop words, stemming
├── extract.py               # Text extraction from PDF, DOCX and TXT
├── templates/
│   └── index.html           # Single-page interface (tabs, results, export)
├── tests/
│   └── test_similarity.py   # Unit tests (pytest)
├── requirements.txt         # Runtime dependencies (minimum versions)
├── requirements-dev.txt     # Runtime + testing dependencies
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.12 or 3.13.** Very new versions (such as 3.15) may not be supported by every library yet.
- **pip** (included with Python).
- An internet connection (required for the internet-check mode).

### Installation

1. **Get the project.**

   ```bash
   git clone https://github.com/<your-username>/plagiarism-checker.git
   cd plagiarism-checker
   ```

   If you downloaded a ZIP file, open the extracted folder that directly contains `app.py`.

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

   If `ddgs` fails to install you can ignore it. The app falls back to another DuckDuckGo method, and Wikipedia search works either way.

4. **Run the app.**

   ```bash
   python app.py
   ```

5. **Open** <http://127.0.0.1:5000> in your browser.

No extra downloads are required: stop words come from scikit-learn, and the Porter stemmer needs no data files.

## Usage

### Compare two documents

1. Open the **Compare two documents** tab.
2. Type, paste or upload Document A and Document B (at least 5 words each).
3. Click **Compare documents**.
4. Read the similarity percentage and the High / Moderate / Low result. Matching 4-word sequences are highlighted in both texts.

### Check against the internet

1. Open the **Check against the internet** tab.
2. Type, paste or upload your text (at least 8 words).
3. Optionally tick **Save this text to the database**. The text is stored only if the box is ticked.
4. Click **Check against the internet** and wait up to about a minute.
5. Read the result, the table of matching sources, and the highlighted text.

### Export

After a result appears, use **Download PDF report** (choose *Save as PDF* in the print window) or **Download text report (.txt)**.

### Clearing the database

*Clear database* is available in the footer. Locally it works directly. On a deployed server it works only when the `ADMIN_KEY` environment variable is set, and the key must be typed in.

## Running the Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

The tests cover: identical documents scoring 100%, different documents scoring near 0%, the 70 / 40 classification rules, Jaccard similarity, removal of citation markers, shared 4-gram detection, the wording of the web-check results, and comparison against stored documents.

## Deployment (Render)

1. Push the project to GitHub. Do not upload `venv/`, `__pycache__/` or `history.db`.
2. On [render.com](https://render.com), create a **New Web Service** from the repository and use:

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --timeout 120` |
| Instance Type | Free |
| Environment variable | `PYTHON_VERSION` = `3.12.7` |
| Environment variable (optional) | `ADMIN_KEY` = a secret used to clear the database |

3. Render redeploys automatically on every commit.

The `--timeout 120` option matters: the internet check can take longer than gunicorn's default 30 seconds. The database table is created automatically when the app starts, so no extra setup is needed.

On the free plan the service sleeps after inactivity and takes about a minute to wake up. The SQLite file may also be reset when the service restarts, so saved documents are not permanent there.

## Configuration

Settings at the top of `webcheck.py` and `app.py`:

| Setting | File | Default | Meaning |
|---|---|---|---|
| `N` | `webcheck.py`, `app.py` | `4` | Words per shingle (n-gram size) |
| `MAX_QUERIES` | `webcheck.py` | `5` | Sentences searched online |
| `MAX_PAGES` | `webcheck.py` | `10` | Maximum pages downloaded per check |
| `MAX_CONTENT_LENGTH` | `app.py` | 10 MB | Maximum upload size |
| `ADMIN_KEY` | environment | empty | Secret needed to clear the database on a server |

The 70 / 40 rules are in `classify()` in `similarity.py`. The web-check thresholds (15% and 40%) are in `verdict()` in `webcheck.py`.

## Security and Privacy

- **SQL injection:** all database queries use parameters (`?`).
- **XSS:** user text is escaped before highlighting is added.
- **Uploads:** only `.pdf`, `.docx` and `.txt` are processed, with a 10 MB limit and safe handling of unreadable files.
- **Privacy:** texts are **not** stored unless the user ticks the save box, and the interface warns not to save confidential documents.
- **Database clearing** is disabled on servers unless an admin key is configured.
- External links open with `rel="noopener"`.

## Limitations

- The internet check finds **copied wording** only. It does not recognize paraphrasing or translation.
- Only **5 sentences** of a text are searched online, so in a long document (for example 10 pages) most of the text is never searched.
- Results depend on search-engine results, which may be blocked or rate-limited.
- Only **public web pages** are read. Paywalled, login-protected and image-only (scanned) content is not checked.
- The Porter stemmer works for English only, so Somali words are not stemmed correctly (stop words for Somali are included).
- SQLite files on Render's free plan are not permanent. A production system would use PostgreSQL.
- The similarity percentage is an indicator, not proof of plagiarism.

## Future Improvements

- PostgreSQL for permanent storage
- Semantic similarity with language models (for example BERT embeddings) to detect paraphrasing
- Searching more sentences, or the whole text, for long documents
- A Somali stemmer and wider Somali language support
- User accounts and private history
- Rate limiting for public deployments
- Server-generated PDF reports

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python, tick **Add python.exe to PATH**, then reopen the terminal |
| `No module named flask` | Activate the virtual environment and run `python -m pip install -r requirements.txt` |
| `TemplateNotFound: index.html` | The file must be at `templates/index.html` |
| Old design or icon shown | Hard refresh with Ctrl + F5, or open a private window |
| "No results were found on the internet" | Check your connection and try again. Search engines can occasionally block requests |
| "No text could be read from this file" | The PDF is probably a scan (an image). Use a text-based PDF or paste the text |
| "The file is too large" | The limit is 10 MB |
| "Clearing the database is disabled" | Set the `ADMIN_KEY` environment variable on the server |
| Render deploy fails | Open the deploy **Logs** and check `PYTHON_VERSION`, `requirements.txt` and the Start Command |

## Change Log

### Version 1.1 (supervisor review fixes)

- **New:** *Compare two documents* mode using TF-IDF and cosine similarity, with the 70 / 40 IF-THEN rules (`classify()`). The internet check is now an additional feature.
- **Changed:** results are reported as *High / Moderate / Low Similarity* instead of "Plagiarized", with a notice that the tool measures similarity only.
- **Fixed (Bug 1):** a text is no longer compared with its own saved copy, and duplicates are not stored twice.
- **Fixed (Bug 2):** removed the NLTK stop-word download; stop words now come from scikit-learn, so the app always starts.
- **Fixed (Bug 5):** documented `gunicorn app:app --timeout 120`, and the database table is created at startup.
- **Added (Bug 6):** 10 MB upload limit with a clear error message.
- **Fixed (Bug 7):** scanned PDFs now show a clear message instead of "too short".
- **Privacy:** saving to the database is optional (checkbox), with a visible notice.
- **Security:** database clearing is protected by an admin key on servers.
- **Tests:** added 8 pytest unit tests and `requirements-dev.txt`.
- **Dependencies:** minimum versions added to `requirements.txt`.
- **Performance:** `overlap_score()` no longer rebuilds a set on every iteration.

### Version 1.0

- Internet check with Wikipedia and DuckDuckGo, 4-gram matching, highlighting, SQLite storage, PDF and text export, Render deployment.

## Authors

| Name | Role |
|---|---|
| Amiin Abdalla | Project lead, deployment (GitHub, Render), testing |
| *(Mohamed yusuf gas)* | 	Documentation (Proposal, Chapters) iyo tijaabada |
| *(Cusmaan Ayaanle)* | Backend (Flask, algorithm)|
| *(Mohamoud mohamed shabelle)* | Interface iyo naqshada (HTML, CSS) |

Developed as a university project: *Document Plagiarism Checker using Text Similarity Matching*.

**Authorship and AI assistance.** Replace this paragraph with a statement that matches your university's rules. For example: *"The group designed the system and wrote the documentation. An AI assistant (Claude, by Anthropic) was used to help write and debug parts of the code, and all group members reviewed and tested the result and can explain every part of it."*

> This project was built for academic purposes. Add a license file (for example MIT) before reusing or redistributing it.
