# Taylor Swift's Discography Database

## ER Model schema
// Entidades
Album(
  _ id _,
  titulo,
  url,
  categoria
)

Musica(
  _ id _,
  track_number,
  titulo,
  url,
  data_lancamento,
  visualizacoes,
  lyrics
)

Pessoa(
  _ id _,
  nome
)

Tag(
  _ id _,
  nome
)

// Relacionamentos

// Album contém Músicas (1:N, total:parcial)
Album === 1 === < contem > --- N --- Musica

// Pessoa interpreta Músicas (M:N, parcial:parcial)
Pessoa --- M --- < interpreta > --- N --- Musica

// Pessoa escreve Músicas (M:N, parcial:parcial)
Pessoa --- M --- < escreve > --- N --- Musica

// Pessoa produz Músicas (M:N, parcial:parcial)
Pessoa --- M --- < produz > --- N --- Musica

// Música classificada com Tags (M:N, parcial:parcial)
Musica --- M --- < classificada_com > --- N --- Tag


## Relational Model schema
table Album
(
  _ id _,
  titulo,
  url,
  categoria
)

table Musica
(
  _ id _,
  track_number,
  titulo,
  url,
  data_lancamento,
  visualizacoes,
  lyrics,
  album_id --> Album.id
)

table Pessoa
(
  _ id _,
  nome
)

table Tag
(
  _ id _,
  nome
)

table Interpreta
(
  _ pessoa_id _ --> Pessoa.id,
  _ musica_id _ --> Musica.id
)

table Escreve
(
  _ pessoa_id _ --> Pessoa.id,
  _ musica_id _ --> Musica.id
)

table Produz
(
  _ pessoa_id _ --> Pessoa.id,
  _ musica_id _ --> Musica.id
)

table MusicaTag
(
  _ musica_id _ --> Musica.id,
  _ tag_id _ --> Tag.id
)
