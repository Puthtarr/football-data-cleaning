import os
from pathlib import Path

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


#https://www.kaggle.com/datasets/davidcariboo/player-scores/data
