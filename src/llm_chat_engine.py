import os
import platform
import gdown
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase

# Load ENV only run in local
if os.environ.get("STREAMLIT_SERVER_ENABLED") is None:
    load_dotenv()

# Load Api key from env
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

if not api_key or not api_base:
    raise ValueError("OPENAI_API_KEY or OPENAI_API_BASE not define in environment variables")

# Load database path
def download_db_path():
    if platform.system() == "Windows":
        return "D:/Data Project/exercise/Football/database/clean_football.db"
    else:
        # for Streamlit Cloud or Linux
        db_path = "/tmp/clean_football.db"
        if not os.path.exists(db_path):
            file_id = "1Kpv8ySZh-0SHgmSftHbtdgxji8KQEpRz"
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, db_path, quiet=False)
        return db_path

def get_db_path():
    return download_db_path()

# Connect database
db_path = get_db_path()
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# set LLM from OpenRouter (Claude 3 Haiku)
llm = ChatOpenAI(
    model="anthropic/claude-3-haiku",
    temperature=0,
    openai_api_key=api_key,
    openai_api_base=api_base,
)

# Prompt for SQL query only
prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are an intelligent assistant that answers questions using data from a football SQLite database.

Here is the schema of the database:

Table: appearances
- appearance_id: TEXT
- game_id: INTEGER
- player_id: INTEGER
- player_club_id: INTEGER
- date: TIMESTAMP
- goals: INTEGER
- assists: INTEGER
- yellow_cards: INTEGER
- red_cards: INTEGER
- minutes_played: INTEGER

Table: clubs
- club_id: INTEGER
- name: TEXT

Table: players
- player_id: INTEGER
- name: TEXT
- current_club_id: INTEGER

Table: games
- game_id: INTEGER
- date: TIMESTAMP
- home_club_id: INTEGER
- away_club_id: INTEGER
- home_club_goals: INTEGER
- away_club_goals: INTEGER
- home_club_name: TEXT
- away_club_name: TEXT

Table: transfers
- player_id: INTEGER
- transfer_date: DATE
- from_club_id: INTEGER
- to_club_id: INTEGER
- transfer_fee: INTEGER
- market_value_in_eur: INTEGER

If you need to get the club name from a `club_id`, join with the `clubs` table on `club_id`.
If you want to get player stats, use the `appearances` table.
If you want to get total goals by a club, sum `goals` in `appearances` where `player_club_id = club_id`.

When converting questions to SQL, always ensure the column and table names exist.

Follow these strict rules:

1. If the question asks about number of goals scored, always use SUM(goals).
2. Never use LIMIT unless the user says "top N" or "most recent N".
3. Always use player_name LIKE '%<name>%' to match players.
4. When a season like "2021/2022" is mentioned, treat it as date BETWEEN '2021-07-01' AND '2022-06-30'.
5. All goal data is stored in the table named appearances.
6. If the user asks about a team like "Liverpool", first find the club_id from table clubs WHERE name LIKE '%Liverpool%', then use that club_id in appearances.player_club_id.
7. Always reply in Thai with human-friendly answer (e.g., "ลิเวอร์พูล ยิงได้ 85 ประตูในฤดูกาล 2021/22")

Write only the final answer in Thai, ignore SQL output.

Question: {input}
"""
)

# Create Chain
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=prompt,
    return_intermediate_steps=False,
    verbose=True
)

def get_llm_chain():
    return db_chain
