import os
from pathlib import Path
import platform
import gdown
import streamlit as st

project_root = Path(__file__).resolve().parent
# print(project_root)

db_path = project_root / "database"
os.makedirs(db_path, exist_ok=True)

images_path = project_root / "images"
os.makedirs(images_path, exist_ok=True)

player_images_path = images_path / "player"
os.makedirs(player_images_path, exist_ok=True)

pages_path = project_root / 'pages'
os.makedirs(pages_path, exist_ok=True)

@st.cache_resource
def download_db_path():
    if platform.system() == "Windows":
        return "D:/Data Project/exercise/Football/database/clean_football.db"
    else:
        # สำหรับ Streamlit Cloud หรือ Linux
        db_path = "/tmp/clean_football.db"
        if not os.path.exists(db_path):
            file_id = "1Kpv8ySZh-0SHgmSftHbtdgxji8KQEpRz"  # ของคุณ
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, db_path, quiet=False)
        return db_path

@st.cache_resource
def get_db_path():
    return download_db_path()

#https://www.kaggle.com/datasets/davidcariboo/player-scores/data
