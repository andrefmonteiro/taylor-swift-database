
CREATE TABLE Album (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    url TEXT,
    categoria TEXT
);

CREATE TABLE Musica (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_number INTEGER,
    titulo TEXT NOT NULL,
    url TEXT,
    data_lancamento DATE,
    visualizacoes INTEGER,
    lyrics TEXT,
    album_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES Album(id) ON DELETE CASCADE
);

CREATE TABLE Pessoa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE Tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);


CREATE TABLE Interpreta (
    pessoa_id INTEGER NOT NULL,
    musica_id INTEGER NOT NULL,
    PRIMARY KEY (pessoa_id, musica_id),
    FOREIGN KEY (pessoa_id) REFERENCES Pessoa(id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES Musica(id) ON DELETE CASCADE
);


CREATE TABLE Escreve (
    pessoa_id INTEGER NOT NULL,
    musica_id INTEGER NOT NULL,
    PRIMARY KEY (pessoa_id, musica_id),
    FOREIGN KEY (pessoa_id) REFERENCES Pessoa(id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES Musica(id) ON DELETE CASCADE
);


CREATE TABLE Produz (
    pessoa_id INTEGER NOT NULL,
    musica_id INTEGER NOT NULL,
    PRIMARY KEY (pessoa_id, musica_id),
    FOREIGN KEY (pessoa_id) REFERENCES Pessoa(id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES Musica(id) ON DELETE CASCADE
);


CREATE TABLE MusicaTag (
    musica_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (musica_id, tag_id),
    FOREIGN KEY (musica_id) REFERENCES Musica(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tag(id) ON DELETE CASCADE
);

-- INDICES: do we need this? Do we have bonus points?

CREATE INDEX idx_musica_album ON Musica(album_id);
CREATE INDEX idx_interpreta_musica ON Interpreta(musica_id);
CREATE INDEX idx_interpreta_pessoa ON Interpreta(pessoa_id);
CREATE INDEX idx_escreve_musica ON Escreve(musica_id);
CREATE INDEX idx_escreve_pessoa ON Escreve(pessoa_id);
CREATE INDEX idx_produz_musica ON Produz(musica_id);
CREATE INDEX idx_produz_pessoa ON Produz(pessoa_id);
CREATE INDEX idx_musicatag_musica ON MusicaTag(musica_id);
CREATE INDEX idx_musicatag_tag ON MusicaTag(tag_id);