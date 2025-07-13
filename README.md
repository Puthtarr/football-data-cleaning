
# DeepPlayr – Football Data AI Assistant

**DeepPlayr** is an AI-powered chatbot interface that allows you to explore football data using natural language. It leverages LLMs (LangChain + OpenAI) to convert questions into SQL queries and returns answers based on a cleaned SQLite database sourced from Kaggle and stored on Google Drive.

---

## Dataset Source

> [Kaggle – player-scores dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores)

This dataset provides player performance data that we clean and transform into a structured database for interactive AI queries.

---

## Features

- Ask football-related questions in natural language (Demo)
- Convert questions to SQL using LLM (LangChain + OpenAI)
- Use cleaned SQLite database stored on Google Drive
- Interactive web-based UI built with Streamlit
- Support for player image downloads and display (Next phase)

---

## Tech Stack

- Python 3.10+
- Pandas – for data cleaning
- LangChain + OpenAI – natural language to SQL
- SQLite – structured data storage
- Google Drive – stores the `.db` file
- Streamlit – web interface
- dotenv – config management

---

## Project Structure

```
Football/
├── database/
│   ├── clean_football.db              # Cleaned SQLite DB (uploaded to GDrive)
│   └── Football.db                    # Raw DB from Kaggle CSV
│
├── images/
│   ├── player/                        # Player profile images
│   └── DeepPlayr_logo.png
│
├── pages/
│   ├── chat_interface.py              # AI Chat main page
│   ├── player_bio.py
│   ├── player_stat.py
│   └── player_transfer.py
│
├── src/
│   ├── download_csv_from_kaggle.py    # Step 1: Download raw data from Kaggle
│   ├── clean_data.py                  # Step 2: Clean and save to clean_football.db, upload to GDrive
│   ├── download_players_image.py      # (Optional) Download player images
│   ├── llm_chat_engine.py             # LangChain SQL Agent
│   └── test.py                        # Prompt/SQL testing
│
├── main.py
├── settings.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/your-username/deepplayr.git
cd deepplayr
pip install -r requirements.txt
```

---

## Environment Variables (`.env`)

```env
OPENAI_API_KEY=sk-xxxxxxx
OPENAI_API_BASE=https://openrouter.ai/api/v1
DATABASE_PATH=/path/to/clean_football.db or GDrive mount path
```

> If using Google Drive, mount it locally or in Colab and point to the path of the `.db` file.

---

## Workflow

### Step 1: Download raw data from Kaggle

```bash
python src/download_csv_from_kaggle.py
```

- Downloads `players.csv`, `transfers.csv`, etc.
- Converts to SQLite → `database/Football.db`

---

### Step 2: Clean and upload data

```bash
python src/clean_data.py
```

- Clean data using Pandas:
  - Parse `transfer_fee`, format `dates`, handle missing values
- Save cleaned database as `clean_football.db`
- Upload to Google Drive (manual or via `gdown`, etc.)

---

### (Optional) Download player images
- in development process cannot find library that can help
```bash
python src/download_players_image.py
```

- Downloads images and stores them in `images/player/`
- Used for player profile pages

---

## Run the Web App

```bash
streamlit run pages/chat_interface.py
```

Ask any football-related question, e.g.:

- "How many goals did Haaland score in 2023?"
- "Who transferred out of Manchester United in 2021?"

---


Use this script to test prompts and SQL output directly.

---


## 🧠 Future Improvements

- Player comparison charts and visualizations
- ML-powered player recommendation
- Big data support: DuckDB, BigQuery, etc.
- Multi-language support (EN/TH)

---

## 👤 Author

Piyaphat Putthasangwan  
GitHub: [puthtarr](https://github.com/puthtarr)

---

## 📜 License

MIT License – For educational and portfolio use
