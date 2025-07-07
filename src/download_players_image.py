import sqlite3
import pandas as pd
import wikipedia
import requests
import os

DB_PATH = r"D:\Data Project\exercise\Football\database\clean_football.db"

def get_player_name():
    conn = sqlite3.connect(DB_PATH)
    sql = "SELECT player_id, name FROM players"
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def download_from_wikipedia(name, save_dir="images"):
    wikipedia.set_lang("en")
    try:
        search_results = wikipedia.search(name)
        if not search_results:
            print(f"❌ Not found: {name}")
            return None

        try:
            page = wikipedia.page(search_results[0], auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            print(f"⚠️ Ambiguous for {name}, using: {e.options[0]}")
            page = wikipedia.page(e.options[0])

        # เลือกรูป usable
        images = [img for img in page.images if img.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not images:
            print(f"❌ No usable image for {name}")
            return None

        image_url = images[0]
        response = requests.get(image_url, timeout=10)

        if response.status_code == 200:
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, f"{name.replace(' ', '_')}.jpg")
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ {name} → {file_path}")
            return file_path
        else:
            print(f"❌ Failed to download image for {name}")
            return None

    except Exception as e:
        print(f"❌ Error for {name}: {e}")
        return None

def main():
    df = get_player_name()
    downloaded = []

    for name in df['name'].dropna().unique():
        path = download_from_wikipedia(name)
        if path:
            downloaded.append((name, path))
            print(f"✅ {name} → {path}")

    pd.DataFrame(downloaded, columns=['name', 'image_path']).to_csv("image_paths.csv", index=False)

if __name__ == "__main__":
    main()
