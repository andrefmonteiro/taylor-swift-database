"""
TODO
[] create taylow_swift.db
[] execute schema.sql
[] read dataset-ts_discography.tsv
[] clean data: delete duplicates
[] insert into every table
"""


import sys
from datetime import datetime
import ast
import sqlite3
import pandas as pd

# Configuração
DB_FILE = 'taylor_swift.db'
SCHEMA_FILE = 'schema.sql'
DATASET_FILE = '../dataset-files/dataset-ts_discography.tsv'


def create_database():
    """Creates database and executes the SQL schema."""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    conn.commit()
    return conn, cursor


def parse_list_field(field):
    """
    Processes fields that contain lists in a string format
    E.g. "['Taylor Swift', 'Max Martin']" -> ['Taylor Swift', 'Max Martin']
    """
    if pd.isna(field) or field == '':
        return []
    try:
        return ast.literal_eval(field)
    except:
        return []


def process_albums(df, cursor):
    """
    Processes and inserts unique albums in the DB.
    Returns dictionary: {(titulo, url): id}
    """

    albums = df[['album_title', 'album_url', 'category']].drop_duplicates()

    album_map = {}  # (titulo, url) -> id

    for _, row in albums.iterrows():
        cursor.execute("""
            INSERT INTO Album(titulo, url, categoria)
            VALUES(?, ?, ?)
        """, (row['album_title'], row['album_url'], row['category']))

        album_id = cursor.lastrowid
        album_map[(row['album_title'], row['album_url'])] = album_id

    return album_map


def process_people(df, cursor):
    """
    Processes and inserts unique people (artists, writers, producers).
    Returns dictionary: {nome: id}
    """

    pessoas = set()

    for _, row in df.iterrows():

        artists = parse_list_field(row['song_artists'])
        pessoas.update(artists)

        writers = parse_list_field(row['song_writers'])
        pessoas.update(writers)

        producers = parse_list_field(row['song_producers'])
        pessoas.update(producers)

    # Remove empty strings
    pessoas = {p for p in pessoas if p and p.strip()}

    pessoa_map = {}  # nome -> id

    for nome in sorted(pessoas):
        cursor.execute("""
            INSERT INTO Pessoa (nome)
            VALUES (?)
        """, (nome,))

        pessoa_id = cursor.lastrowid
        pessoa_map[nome] = pessoa_id

    return pessoa_map


def process_tags(df, cursor):
    """
    Processes and inserts unique tags.
    Returns dictionary: {nome: id}
    """

    tags = set()

    for _, row in df.iterrows():
        song_tags = parse_list_field(row['song_tags'])
        tags.update(song_tags)

    # Remove empty strings
    tags = {t for t in tags if t and t.strip()}

    tag_map = {}  # nome -> id

    for nome in sorted(tags):
        cursor.execute("""
            INSERT INTO Tag (nome)
            VALUES (?)
        """, (nome,))

        tag_id = cursor.lastrowid
        tag_map[nome] = tag_id

    return tag_map


def parse_date(date_str):
    """
    Converts date string to SQLite format (YYYY-MM-DD).
    E.g. "6/19/2006" -> "2006-06-19"
    """
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        # assuming M/D/YYYY
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except:
        try:
            # assuming already correct yyyy/mm/dd
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except:
            return None


def process_songs(df, cursor, album_map, pessoa_map, tag_map):
    """
    Processes and inserts songs and relationships.
    """

    musica_count = 0
    interpreta_count = 0
    escreve_count = 0
    produz_count = 0
    musicatag_count = 0

    for _, row in df.iterrows():
        # Get album_id
        album_key = (row['album_title'], row['album_url'])
        album_id = album_map.get(album_key)

        if not album_id:
            continue

        # Process lyrics
        lyrics_list = parse_list_field(row['song_lyrics'])
        lyrics_text = '\n'.join(lyrics_list) if lyrics_list else None

        # Procesr date
        data_lancamento = parse_date(row['song_release_date'])

        # Insert song
        cursor.execute("""
            INSERT INTO Musica (track_number, titulo, url, data_lancamento, 
                               visualizacoes, lyrics, album_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row['album_track_number'],
            row['song_title'],
            row['song_url'],
            data_lancamento,
            row['song_page_views'],
            lyrics_text,
            album_id
        ))

        musica_id = cursor.lastrowid
        musica_count += 1

        # Insert relationship Interpreta (artistas)
        artists = parse_list_field(row['song_artists'])
        for artist_name in artists:
            if artist_name in pessoa_map:
                cursor.execute("""
                    INSERT INTO Interpreta (pessoa_id, musica_id)
                    VALUES (?, ?)
                """, (pessoa_map[artist_name], musica_id))
                interpreta_count += 1

        # Insert relationship Escreve (escritores)
        writers = parse_list_field(row['song_writers'])
        for writer_name in writers:
            if writer_name in pessoa_map:
                cursor.execute("""
                    INSERT INTO Escreve (pessoa_id, musica_id)
                    VALUES (?, ?)
                """, (pessoa_map[writer_name], musica_id))
                escreve_count += 1

        # Insert relationship Produz (produtores)
        producers = parse_list_field(row['song_producers'])
        for producer_name in producers:
            if producer_name in pessoa_map:
                cursor.execute("""
                    INSERT INTO Produz (pessoa_id, musica_id)
                    VALUES (?, ?)
                """, (pessoa_map[producer_name], musica_id))
                produz_count += 1

        # Insert relationship MusicaTag
        tags = parse_list_field(row['song_tags'])
        for tag_name in tags:
            if tag_name in tag_map:
                cursor.execute("""
                    INSERT INTO MusicaTag (musica_id, tag_id)
                    VALUES (?, ?)
                """, (musica_id, tag_map[tag_name]))
                musicatag_count += 1


def main():

    try:
        conn, cursor = create_database()

        df = pd.read_csv(DATASET_FILE, sep='\t')

        # Process and insert data
        album_map = process_albums(df, cursor)
        pessoa_map = process_people(df, cursor)
        tag_map = process_tags(df, cursor)
        process_songs(df, cursor, album_map, pessoa_map, tag_map)

        conn.commit()
        conn.close()

    except FileNotFoundError as e:
        sys.exit(1)

    except Exception as e:
        print("\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
