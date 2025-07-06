import sqlite3
from settings import *
import os
import pandas as pd

def clean_data():
    print(db_path)
    conn = sqlite3.connect(os.path.join(db_path, 'Football.db'))
    tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    print(tables_df)
    return conn

def clean_appearances(conn):
    # appearances table
    df_appearances = pd.read_sql("SELECT * FROM appearances", conn)
    print(df_appearances.head(10))

    # column date to datetime
    df_appearances['date'] = pd.to_datetime(df_appearances['date'], errors='coerce')

    # delete dupplicate rows
    df_appearances = df_appearances.drop_duplicates(subset=['appearance_id'])

    # clean player name
    df_appearances['player_name'] = df_appearances['player_name'].str.strip().str.title()

    # Fill missing value
    cols_to_fill = ['goals', 'assists', 'minutes_played', 'yellow_cards', 'red_cards']
    df_appearances[cols_to_fill] = df_appearances[cols_to_fill].fillna(0)

    # Filter Only not null player_id, game_id
    df_appearances = df_appearances[df_appearances['player_id'].notna() & df_appearances['game_id'].notna()]

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_appearances.to_sql('appearances', conn_clean, index=False, if_exists='replace')

def clean_club_games(conn):
    df_club_games = pd.read_sql(f"SELECT * FROM club_games", conn)
    print(df_club_games.head(10))
    print(df_club_games.dtypes)

    # delete dupplicate rows
    df_club_games = df_club_games.drop_duplicates(subset=['game_id'])

    # clean player name
    df_club_games['own_manager_name'] = df_club_games['own_manager_name'].str.strip().str.title()
    df_club_games['opponent_manager_name'] = df_club_games['opponent_manager_name'].str.strip().str.title()

    # position check (null value is mean it not league game)
    df_club_games['own_position'] = df_club_games['own_position'].fillna(-1).astype(int)
    df_club_games['opponent_position'] = df_club_games['opponent_position'].fillna(-1).astype(int)
    df_club_games['is_league_game'] = df_club_games.apply(
        lambda row: "Yes" if row['own_position'] != -1 and row['opponent_position'] != -1 else "No",
        axis=1
    )

    # dtype
    df_club_games['own_goals'] = df_club_games['own_goals'].fillna(0).astype(int)
    df_club_games['opponent_goals'] = df_club_games['opponent_goals'].fillna(0).astype(int)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_club_games.to_sql('club_games', conn_clean, index=False, if_exists='replace')


def clean_clubs(conn):
    df_clubs = pd.read_sql(f"SELECT * FROM clubs", conn)
    print(df_clubs.dtypes)
    print(df_clubs.head(10))

    # clean net_transfer_record
    def clean_net_transfer_record(col):
        col = col.fillna('0').astype(str)

        # Remove € and +
        col = col.str.replace('€', '', regex=False)
        col = col.str.replace('+', '', regex=False)

        # k → x / 1000
        k_mask = col.str.contains('k', case=False, na=False)
        col[k_mask] = col[k_mask].str.replace('k', '', regex=False).astype(float) / 1000

        # m → x (Million)
        m_mask = col.str.contains('m', case=False, na=False)
        col[m_mask] = col[m_mask].str.replace('m', '', regex=False).astype(float)

        # Clean leftover invalid strings
        col = col.replace(['', '-', '+-0'], '0')

        return col.astype(float)

    df_clubs['net_transfer_record'] = clean_net_transfer_record(df_clubs['net_transfer_record'])
    print(df_clubs['total_market_value'], df_clubs['net_transfer_record'])
    # print(len(df_clubs))

    # delete not use column (meta data)
    col_to_del = ['domestic_competition_id', 'coach_name', 'filename', 'url', 'total_market_value']
    df_clubs = df_clubs.drop(columns=col_to_del)
    print(df_clubs.columns)

    # dtypes
    df_clubs['average_age'] = pd.to_numeric(df_clubs['average_age'], errors='coerce')
    df_clubs['foreigners_percentage'] = pd.to_numeric(df_clubs['foreigners_percentage'], errors='coerce')

    # Stadium name Title
    df_clubs['stadium_name'] = df_clubs['stadium_name'].str.strip().str.title()
    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_clubs.to_sql('clubs', conn_clean, index=False, if_exists='replace')

    # null value
    df_clubs['average_age'] = pd.to_numeric(df_clubs['average_age'], errors='coerce')
    df_clubs['foreigners_percentage'] = pd.to_numeric(df_clubs['foreigners_percentage'], errors='coerce')

    df_clubs[['average_age', 'foreigners_percentage']] = df_clubs[['average_age', 'foreigners_percentage']].fillna(0)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_clubs.to_sql('clubs', conn_clean, index=False, if_exists='replace')

def clean_competitions(conn):
    df_competitions = pd.read_sql(f"SELECT * FROM competitions", conn)
    print(df_competitions)

    # delete metada
    df_competitions = df_competitions.drop(columns='url')

    # UCL match domestic_league_code
    mapping = {
        'uefa_super_cup': 'SUPERCUP',
        'europa_league': 'EUROPA',
        'uefa_europa_conference_league': 'CONFERENCE',
        'europa_league_qualifying': 'EUROPA_QUALIFY',
        'uefa_europa_conference_league_qualifiers': 'CONFERENCE_QUALIFY',
        'uefa_champions_league': 'UCL',
        'fifa_club_world_cup': 'CLUB_WC',
        'uefa_champions_league_qualifying': 'UCL_QUALIFY'
    }

    mask = df_competitions['domestic_league_code'].isnull()
    df_competitions.loc[mask, 'domestic_league_code'] = df_competitions.loc[mask, 'sub_type'].map(mapping)

    # UCL country name
    mapping = {
        'uefa_super_cup': 'EUROPE',
        'europa_league': 'EUROPE',
        'uefa_europa_conference_league': 'EUROPE',
        'europa_league_qualifying': 'EUROPE',
        'uefa_europa_conference_league_qualifiers': 'EUROPE',
        'uefa_champions_league': 'EUROPE',
        'fifa_club_world_cup': 'WC',
        'uefa_champions_league_qualifying': 'EUROPE'
    }

    mask = df_competitions['country_name'].isnull()
    df_competitions.loc[mask, 'country_name'] = df_competitions.loc[mask, 'sub_type'].map(mapping)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_competitions.to_sql('competitions', conn_clean, index=False, if_exists='replace')

def clean_game_events(conn):
    df_game_events = pd.read_sql(f"SELECT * FROM game_events", conn)
    print(df_game_events.dtypes)

    # Schema convert
    df_game_events['date'] = pd.to_datetime(df_game_events['date'], errors='coerce')

    # convert player_in_id and player_assist_id
    df_game_events['player_in_id'] = df_game_events['player_in_id'].fillna('unknown').astype(str)
    df_game_events['player_assist_id'] = df_game_events['player_assist_id'].fillna('unknown').astype(str)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_game_events.to_sql('game_events', conn_clean, index=False, if_exists='replace')

def clean_game_lineups(conn):
    df_game_lineups = pd.read_sql(f"SELECT * FROM game_lineups", conn)
    print(df_game_lineups.columns)
    print(df_game_lineups.dtypes)

    # Schema convert
    df_game_lineups['date'] = pd.to_datetime(df_game_lineups['date'], errors='coerce')
    df_game_lineups['player_name'] = df_game_lineups['player_name'].str.strip().str.title()
    df_game_lineups['team_captain'] = df_game_lineups['team_captain'].fillna(0).astype(int)
    df_game_lineups['number'] = (df_game_lineups['number'].replace('-', 0).replace('', 0).astype(int))

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_game_lineups.to_sql('game_lineups', conn_clean, index=False, if_exists='replace')

def clean_games(conn):
    df_games = pd.read_sql(f'SELECT * FROM games', conn)
    print(df_games.dtypes)

    df_games['season'] = pd.to_datetime(df_games['season'], format='%Y', errors='coerce').dt.year
    df_games['date'] = pd.to_datetime(df_games['date'], errors='coerce')
    df_games['home_club_manager_name'] = df_games['home_club_manager_name'].str.strip().str.title()
    print(df_games['season'])
    print(df_games.dtypes)
    df_games.drop(columns='url', inplace=True)

    # fill na (float)
    df_games[['home_club_id', 'away_club_id', 'home_club_goals',
              'away_club_goals', 'home_club_position',
              'away_club_position', 'attendance']] = df_games[['home_club_id', 'away_club_id', 'home_club_goals',
              'away_club_goals', 'home_club_position',
              'away_club_position', 'attendance']].fillna(-1)

    df_games = df_games.dropna(subset=['home_club_id'])
    df_games.fillna('-', inplace=True)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_games.to_sql('games', conn_clean, index=False, if_exists='replace')


def clean_player_valuations(conn):
    df_value = pd.read_sql(f'SELECT * FROM player_valuations', conn)
    print(df_value.dtypes)
    df_value['date'] = pd.to_datetime(df_value['date'], errors='coerce')

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_value.to_sql('player_valuations', conn_clean, index=False, if_exists='replace')

def clean_players(conn):
    df_players = pd.read_sql(f'SELECT * FROM players', conn)
    print(df_players.dtypes)

    df_players['first_name'] = df_players['first_name'].fillna('')
    df_players['country_of_birth'] = df_players['country_of_birth'].fillna('Unknown')
    df_players['city_of_birth'] = df_players['city_of_birth'].fillna('Unknown')
    df_players['country_of_citizenship'] = df_players['country_of_citizenship'].fillna('Unknown')
    df_players['sub_position'] = df_players['sub_position'].fillna('Missing')
    df_players['foot'] = df_players['foot'].fillna('Unknown')
    df_players['height_in_cm'] = df_players['height_in_cm'].fillna(-1).astype(int)
    df_players['agent_name'] = df_players['agent_name'].fillna('Unknown')
    df_players['market_value_in_eur'] = df_players['market_value_in_eur'].fillna(-1)
    df_players['highest_market_value_in_eur'] = df_players['highest_market_value_in_eur'].fillna(-1)

    placeholder_date = pd.Timestamp('1900-01-01').date()
    df_players['date_of_birth'] = pd.to_datetime(df_players['date_of_birth'], errors='coerce').dt.date
    df_players['date_of_birth'] = df_players['date_of_birth'].fillna(placeholder_date)

    df_players.drop(columns=['contract_expiration_date', 'image_url', 'url'], inplace=True)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_players.to_sql('players', conn_clean, index=False, if_exists='replace')

def clean_transfers(conn):
    df_transfers = pd.read_sql(f'SELECT * FROM transfers', conn)
    print(df_transfers.dtypes)

    # convert to datetime col
    df_transfers['transfer_date'] = pd.to_datetime(df_transfers['transfer_date'], errors='coerce').dt.date

    # Convert string to float first, then fillna, then to int
    df_transfers['transfer_fee'] = pd.to_numeric(df_transfers['transfer_fee'], errors='coerce')
    df_transfers['transfer_fee'] = df_transfers['transfer_fee'].fillna(-1).astype(int)

    df_transfers['market_value_in_eur'] = pd.to_numeric(df_transfers['market_value_in_eur'], errors='coerce')
    df_transfers['market_value_in_eur'] = df_transfers['market_value_in_eur'].fillna(-1).astype(int)

    conn_clean = sqlite3.connect(os.path.join(db_path, 'clean_football.db'))
    df_transfers.to_sql('transfers', conn_clean, index=False, if_exists='replace')


if __name__ == "__main__":
    conn = clean_data()
    # clean_appearances(conn)
    # clean_club_games(conn)
    # clean_clubs(conn)
    # clean_competitions(conn)
    # clean_game_events(conn)
    # clean_game_events(conn)
    # clean_game_lineups(conn)
    clean_games(conn)
    # clean_player_valuations(conn)
    # clean_players(conn)
    # clean_transfers(conn)

