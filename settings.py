import os
from pathlib import Path

project_root = Path(__file__).resolve().parent

db_path = project_root / "database"
os.makedirs(db_path, exist_ok=True)

#https://www.kaggle.com/datasets/davidcariboo/player-scores/data
