# AI Data Analyst Chatbot 🤖📊

> A powerful, AI-driven data analysis platform that lets you interact with datasets using natural language. Built with Flask and Groq AI, it transforms complex analyses into simple conversational queries.

---

## 🚀 Features

* **AI-Powered Analysis**

  * Natural language queries: Ask questions about your data in plain English.
  * Automated code generation: Get Python / pandas code for each analysis.
  * Smart insights: AI-generated patterns and actionable recommendations.
  * Real-time processing with Groq’s high-speed inference.

* **Data Management**

  * Multi-format support: CSV and Excel (`.xlsx`, `.xls`).
  * Automatic preprocessing: Cleaning and type detection.
  * Data quality assessment and recommendations.
  * Analysis history with search and session tracking.

* **User Experience**

  * Modern responsive UI built with Tailwind CSS.
  * Interactive dashboard and visualizations.
  * Smooth floating animations and a dark/light theme toggle.

* **Advanced**

  * Export results and generated code.
  * Session-based collaboration-ready architecture.
  * Multiple AI models supported via Groq.

---

##  Project Structure

```
ai-data-analyst/
├── app.py                 # Main Flask application
├── utils.py               # Data processing utilities
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── analysis_history.json  # Analysis session storage
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── analyze.html
    ├── history.html
    ├── insights.html
    ├── settings.html
    └── help.html
```

---

## 🔄 Workflow

1. Upload dataset (CSV / Excel).
2. Ask natural language questions in the analysis UI.
3. The AI pipeline interprets the query, runs analysis, and returns results + generated pandas code.
4. View insights, visualizations, and save/export results.

---

## 🛠️ Installation & Setup

**Prerequisites**

* Python 3.8+
* Groq API key
* Modern web browser

**Clone the repository**

```bash
git clone https://github.com/Pragyan2004/AI-Data-Analyst-Chatbot.git
cd ai-data-analyst
```


**Environment configuration**

```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env
echo "DEBUG=True" >> .env
```

**Run the application**

```bash
python app.py
```

Open your browser at `http://localhost:5000`.

---

## 📖 Usage Guide

1. Click **Analyze** and upload a CSV / Excel file (max 50MB).
2. Type a plain-English question, e.g.:

   * "Show me summary statistics"
   * "How many missing values are there?"
   * "What's the correlation between age and income?"
   * "Group by category and show averages"
3. Review results, get the generated pandas code, and export if needed.

---

## 🔧 Configuration

**Environment variables** (`.env`)

```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Available AI Models**

* `llama-3.3-70b-versatile` (recommended)
* `llama-3.1-8b-instant`
* `mixtral-8x7b-32768`

---

## 🚀 API Endpoints

| Endpoint     |    Method | Description                              |
| ------------ | --------: | ---------------------------------------- |
| `/`          |       GET | Home page                                |
| `/analyze`   | GET, POST | Data analysis interface (upload + query) |
| `/dashboard` |       GET | Analytics dashboard                      |
| `/insights`  |       GET | AI-generated insights                    |
| `/history`   |       GET | Analysis history                         |
| `/settings`  | GET, POST | User settings                            |
| `/help`      |       GET | Documentation                            |

---

## 🛠️ Technology Stack

* **Backend:** Flask
* **Data:** pandas, OpenPyXL, CSV
* **AI / NLP:** Groq AI
* **Frontend:** Tailwind CSS, vanilla JavaScript, Font Awesome
* **Env:** python-dotenv

---

## 📊 Performance Metrics (Target)

* Query response time: < 2 seconds
* File processing: up to 50MB
* API success rate: 98%+
* Concurrent sessions: multiple (session-based)

---
## 📸 Screenshots

<img width="1457" height="865" alt="Screenshot 2025-09-28 160945" src="https://github.com/user-attachments/assets/014f9302-702d-4b55-8578-8042660875ed" />

<img width="1456" height="808" alt="Screenshot 2025-09-28 160912" src="https://github.com/user-attachments/assets/7744f7f4-950f-4ce4-bd54-1b6f2321b6a8" />

<img width="1540" height="752" alt="Screenshot 2025-09-28 160901" src="https://github.com/user-attachments/assets/6b201bba-7a8d-495f-9381-0f2c3bc8a5ec" />

<img width="1582" height="884" alt="Screenshot 2025-09-28 160849" src="https://github.com/user-attachments/assets/cf282a5f-427d-47ef-93dd-a3c1decb25bf" />

<img width="1682" height="784" alt="Screenshot 2025-09-28 160822" src="https://github.com/user-attachments/assets/17968df8-a64e-460e-b77b-39d575290b6b" />

<img width="1531" height="858" alt="Screenshot 2025-09-28 160753" src="https://github.com/user-attachments/assets/97d112cb-cffe-49c9-9c6e-21c2dfe0e4d8" />

<img width="1900" height="864" alt="Screenshot 2025-09-28 160733" src="https://github.com/user-attachments/assets/d3245460-1ca0-4f29-a291-a6cf621d6192" />

<img width="1899" height="865" alt="Screenshot 2025-09-28 160700" src="https://github.com/user-attachments/assets/2ea793e2-25cc-4a77-8eea-4fa4e0555489" />

---


