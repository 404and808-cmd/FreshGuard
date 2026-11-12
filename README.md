
# 🛡️ FreshGuard
### Temporal Risk Intelligence for AI Gateways

**FreshGuard helps assess claims against retrieved evidence and track how that evidence changes over time.**

AI-generated information can become outdated as sources change, new evidence emerges, or previously reliable information is revised. FreshGuard explores a temporal approach to claim verification by combining evidence retrieval, AI-assisted assessment, source-quality heuristics, and historical evidence comparison.

---

## 🚨 The Problem

Traditional fact-checking often focuses on whether a claim is supported at a particular point in time.

But evidence is not static.

- Sources can be updated or removed.
- New information can contradict earlier findings.
- Previously supported claims can become uncertain.
- AI systems may continue relying on outdated information.

FreshGuard explores how evidence can be monitored across repeated assessments rather than treated as a one-time snapshot.

## 💡 Our Solution

FreshGuard is a temporal evidence intelligence prototype that:

- Extracts claims for verification.
- Retrieves relevant information from external sources.
- Uses an LLM to assist with evidence-based assessment.
- Applies heuristic source-quality scoring.
- Stores evidence snapshots and verification history.
- Compares evidence between assessments.
- Calculates a suggested next-check time based on volatility.

## ⚙️ How It Works

1. **Claim Input:** A user submits a claim for verification.
2. **Evidence Retrieval:** Tavily searches for relevant sources.
3. **AI Assessment:** Gemini assists in evaluating retrieved evidence.
4. **Source Evaluation:** A heuristic system assigns source-quality tiers.
5. **Evidence Storage:** Assessment results and evidence snapshots are stored in SQLite.
6. **Temporal Comparison:** FreshGuard compares current evidence with previous snapshots.
7. **Historical Review:** Users can inspect previous assessments and suggested recheck times.

## 🏗️ System Architecture

```text
                  USER
                    |
                    v
            REACT FRONTEND
                    |
                    v
                 FASTAPI
                    |
           +--------+--------+
           |                 |
           v                 v
       TAVILY API        GEMINI API
     Evidence Search    AI Assessment
           |                 |
           +--------+--------+
                    |
                    v
            SOURCE QUALITY
                SCORING
                    |
                    v
             SQLITE DATABASE
            Evidence Snapshots
            Assessment History
                    |
                    v
             TEMPORAL ANALYSIS
             Evidence Comparison
              Suggested Recheck
                    |
                    v
             DASHBOARD RESULTS
```

## 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, CSS |
| Backend | Python, FastAPI |
| AI | Google Gemini |
| Evidence Retrieval | Tavily |
| Database | SQLite |
| API Communication | REST |
| Version Control | Git, GitHub |

## ✨ Implemented Features

- Claim verification workflow.
- AI-assisted claim assessment.
- External evidence retrieval.
- Heuristic source credibility tiers.
- Evidence snapshot storage.
- Evidence change comparison.
- Historical verification timeline.
- Volatility-based suggested recheck intervals.
- Manual recheck workflow.
- Interactive web dashboard.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js and npm
- Google Gemini API key
- Tavily API key

### 1. Clone the Repository

```bash
git clone https://github.com/404and808-cmd/FreshGuard.git
cd FreshGuard
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory and configure your Gemini and Tavily API keys using the environment variable names expected by the application.

Start the backend server:

```bash
python -m uvicorn app.main:app --reload
```

Backend API:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### 3. Frontend Setup

Open a **second terminal** in the FreshGuard root directory.

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the application:

http://localhost:5173

### 🪟 Windows Troubleshooting

If PowerShell does not recognize `npm` or `npm.cmd`, Node.js may not be available in your system PATH.

**1. Verify Node.js installation**

```powershell
node --version
```

**2. Check npm**

```powershell
npm --version
```

**3. Check the default Node.js installation directory**

```powershell
Test-Path "C:\Program Files\nodejs\npm.cmd"
```

If the result is `True`, temporarily add Node.js to your current PowerShell session:

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
```

**4. Verify npm again**

```powershell
npm.cmd --version
```

**5. Run the frontend**

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

To create a production build:

```powershell
npm.cmd run build
```

**6. If Node.js is not installed**

Download Node.js from:

https://nodejs.org/

Install it, restart PowerShell, and verify:

```powershell
node --version
npm --version
```

**Note:** The PATH modification above is temporary. For a permanent fix, add the Node.js installation directory to your Windows user PATH environment variable.

## 🧪 Testing

Run backend tests from the backend directory:

```bash
python -m pytest -q
```

Build the frontend from the frontend directory:

```bash
npm run build
```

## ⚠️ Current Limitations

FreshGuard is a prototype, not a production-grade fact-checking or continuous monitoring platform.

- Source credibility is based on heuristics and does not guarantee factual accuracy.
- LLM-generated assessments can contain errors.
- Suggested recheck times do not currently represent an automatic background monitoring scheduler.
- Reassessment is initiated manually.
- Evidence retrieval depends on external service availability and search results.

## 🔭 Future Roadmap

- Automated scheduled evidence rechecks.
- Integration with AI gateway infrastructure.
- Real-time evidence drift alerts.
- Stronger source provenance and credibility analysis.
- Improved contradiction detection.
- More comprehensive temporal evidence visualization.
- Evaluation using a curated claim-and-evidence dataset.

## 👥 Team

Built as a hackathon project. Individual Participation.

**Project:** FreshGuard

**GitHub:** https://github.com/404and808-cmd/FreshGuard

---

### FreshGuard
*Because evidence changes, and verification should evolve with it.*
