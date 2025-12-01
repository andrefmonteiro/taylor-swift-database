import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

@APP.route('/')
def index():
    # empty for now
    return render_template('index.html')

# songs_album    -   count the number of songs per album
@APP.route('/songs_album/')
def songs_album():
    albums = db.execute(
      '''
    select a.id, a.titulo as title, count( * ) as songs_count
    from Album as a join Musica as m on m.album_id = a.id
    group by m.album_id;
      ''').fetchall()
    return render_template('songs_album.html', albums=albums)


# only_taylor_writer_songs
@APP.route('/only_taylor_writer_songs/')
def only_taylor_writer_songs():
    songs = db.execute(
      '''
    select m.titulo title
    from Musica m join Escreve e on e.musica_id = m.id
    join Pessoa p on p.id = e.pessoa_id
    group by m.id
    having count(*) = 1 and MAX(p.nome) = 'Taylor Swift';
      ''').fetchall()
    return render_template('only_taylor_writer_songs.html', songs=songs)

# for each song, the name, producer and corresponding tags
@APP.route('/song_producer/')
def song_producer():
    songs = db.execute(
      '''
    select DISTINCT  m.titulo title, p1.nome producer_name
    from Musica as m join Produz as p on p.musica_id = m.id
    join MusicaTag as t on t.musica_id = m.id
    join Pessoa as p1 on p1.id = p.pessoa_id
      ''').fetchall()
    return render_template('song_producer.html', songs=songs)

@APP.route('/songs/<string:word_song>/')
def certain_words(word_song):
    word = word_song.lower()

    songs = db.execute(
        '''
        SELECT 
            m.titulo AS title,
            (LENGTH(lower(m.lyrics)) - LENGTH(REPLACE(lower(m.lyrics), ?, '')))
            / LENGTH(?) AS occurrences
        FROM Musica AS m
        WHERE lower(m.lyrics) LIKE '%' || ? || '%';
        ''',
        [word, word, word]
    ).fetchall()


    return render_template('certain_words.html', songs=songs, word=word_song)

@APP.route('/top_ten_views/')
def top_ten_views():
    songs = db.execute(
      '''
    select m.titulo title, m.visualizacoes views
    from Musica as m
    order by m.visualizacoes desc
    limit 10; 
      ''').fetchall()
    return render_template('top_ten_views.html', songs=songs)

@APP.route('/songs_per_year/')
def songs_per_year():
    songs = db.execute(
      '''
    select strftime('%Y', data_lancamento) as year, count(*) as count
    from Musica
    group by year
    order by year;
      ''').fetchall()
    return render_template('songs_per_year.html', songs=songs)

@APP.route('/oldest_recent_songs/')
def oldest_recent_songs():
    songs = db.execute(
      '''
    select m.data_lancamento date, m.titulo title
    from Musica as m
    where m.data_lancamento = (select max(data_lancamento) from Musica) 
    or m.data_lancamento = (select min(data_lancamento) from Musica);
      ''').fetchall()
    return render_template('oldest_recent_songs.html', songs=songs)

@APP.route('/each_album_info/')
def each_album_info():
    songs = db.execute(
      '''
    with TopSong as (
        select m.id, m.titulo, m.album_id, m.visualizacoes
        from Musica as m
        where m.visualizacoes = (
            select max(m2.visualizacoes)
            from Musica as m2
            where m2.album_id = m.album_id
        )
    )
    select a.id album_id, a.titulo as album, ts.titulo as most_viewed, t.nome as tags
    from Album as a join TopSong as ts on ts.album_id = a.id
    left join MusicaTag mt on mt.musica_id = ts.id
    left join Tag as t  on t.id = mt.tag_id
    group by  a.id, ts.id
    order by album; 
      ''').fetchall()
    return render_template('each_album_info.html', songs=songs)

@APP.route('/songs_views/<int:views>/')
def songs_views(views):
    songs = db.execute(
    '''
    select titulo title, visualizacoes views
    from Musica 
    where visualizacoes > ?;
    ''',
        [views]
    ).fetchall()

    return render_template('songs_views.html', songs=songs, views=views)

@APP.route('/artist_more_one/')
def artist_more_one():
    songs = db.execute(
      '''
    select p2.nome name, count(distinct pr_outro.musica_id) as num
    from Produz as pr_outro join Pessoa as p2 on p2.id = pr_outro.pessoa_id
    join Produz as pr_taylor on pr_taylor.musica_id = pr_outro.musica_id
    join Pessoa as taylor on taylor.id = pr_taylor.pessoa_id
    where taylor.nome = 'Taylor Swift' and p2.nome <> 'Taylor Swift'
    group by p2.id
    having count(distinct pr_outro.musica_id) > 0
    order by num desc;
      ''').fetchall()
    return render_template('artist_more_one.html', songs=songs)


@APP.route('/album/<int:id>/')
def get_album(id):
  album = db.execute(
      '''
      SELECT *
      FROM Album  a
      WHERE a.id = ?
      ''', [id]).fetchone()

  if album is None:
     abort(404, 'album id {} does not exist.'.format(id))

  return render_template('album.html', album=album)

# year.html
@APP.route('/year/<int:year>/')
def get_year(year):
    songs = db.execute(
        '''
        SELECT m.id,
               m.titulo AS title,
               m.url,
               m.data_lancamento AS date,
               m.visualizacoes AS views,
               m.album_id AS album_id
        FROM Musica m
        WHERE strftime('%Y', m.data_lancamento) = ?;
        ''',
        [str(year)]  # convert to string
    ).fetchall()

    if not songs:
        abort(404, f'Year {year} does not exist.')

    return render_template('year.html', year=year, songs=songs)
