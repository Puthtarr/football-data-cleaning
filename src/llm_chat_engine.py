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
You are a Thai-speaking data analyst working with football statistics.

Follow these strict rules:

1. If the question asks about number of goals scored, always use SUM(goals).
2. Never use LIMIT unless the user says "top N" or "most recent N".
3. Always use player_name LIKE '%<name>%' to match players.
4. When a season like "2021/2022" is mentioned, treat it as date BETWEEN '2021-07-01' AND '2022-06-30'.
5. All goal data is stored in the table named appearances.
6. Write only the SQL query. No explanation or other output.

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
