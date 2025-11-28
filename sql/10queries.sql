--Pergunta 1 Quantas músicas tem cada álbum da Taylor Swift 
SELECT a.titulo AS titulo_album, count( * ) AS numero_de_musicas
  FROM Album AS a JOIN Musica AS m ON m.album_id = a.id
 GROUP BY m.album_id;
 
--Pergunta 2 Quais as músicas que foram escritas apenas pela Taylor Swift 

SELECT m.titulo
FROM Musica m JOIN Escreve e ON e.musica_id = m.id
JOIN Pessoa p ON p.id = e.pessoa_id
GROUP BY m.id
HAVING COUNT(*) = 1 AND MAX(p.nome) = 'Taylor Swift';

--Pergunta 3 Quais os produtores e as tags de cada música 

select m.titulo, p1.nome, t1.nome
from Musica as m join Produz as p on p.musica_id = m.id
join MusicaTag as t on t.musica_id = m.id
join Pessoa as p1 on p1.id = p.pessoa_id
join Tag as t1 on t1.id = t.tag_id
group by m.id;

--Pergunta 4 Quais as músicas com a palavra “like” e quantas vezes nessas músicas aparece a palavra “love”  
select m.titulo, (length(lower(m.lyrics)) - length(replace(lower(m.lyrics), 'love', '')))
/length('love') as ocorr_love
from Musica as m
where lower(m.lyrics) like '%like%';

--Pergunta 5a) Quais as 10 músicas com mais vizualizações
select m.titulo, m.visualizacoes
from Musica as m
order by m.visualizacoes desc
limit 10; 
--Pergunta 5b)Número de músicas por ano lançamento
select strftime('%Y', data_lancamento) as ano, count(*) as n_músicas
from Musica
group by ano
order by ano;

--Pergunta 6 Qual é a música e qual a data da música publicada mais recentemente e  da música publicada há mais tempo 

select m.data_lancamento, m.titulo
from Musica as m
where m.data_lancamento = (select max(data_lancamento) from Musica) 
or m.data_lancamento = (select min(data_lancamento) from Musica);

--Pergunta 7 Qual é o nome de cada álbum, sua tag e a música com mais visualizações 
--música mais popular por album
with TopSong as (
    select m.id, m.titulo, m.album_id, m.visualizacoes
    from Musica as m
    where m.visualizacoes = (
        select max(m2.visualizacoes)
        from Musica as m2
        where m2.album_id = m.album_id
    )
)
select a.titulo as album, ts.titulo as musica_mais_vista, t.nome as tags
from Album as a join TopSong as ts on ts.album_id = a.id
left join MusicaTag mt on mt.musica_id = ts.id
left join Tag as t  on t.id = mt.tag_id
group by  a.id, ts.id
order by album; 

--Pergunta 8 Quais as músicas com mais de 100000 visualizações
select titulo, visualizacoes
from Musica 
where visualizacoes > 100000;

--Pergunta 9  Quais são os artistas que produziram mais do que uma música juntamente com a Taylor 
select p2.nome, count(distinct pr_outro.musica_id) as num_musicas_com_Taylor
from Produz as pr_outro join Pessoa as p2 on p2.id = pr_outro.pessoa_id
join Produz as pr_taylor on pr_taylor.musica_id = pr_outro.musica_id
join Pessoa as taylor on taylor.id = pr_taylor.pessoa_id
where taylor.nome = 'Taylor Swift' and p2.nome <> 'Taylor Swift'
group by p2.id
having count(distinct pr_outro.musica_id) > 1
order by num_musicas_com_Taylor desc;

--Pergunta 10 Qual a música com a letra mas comprida de cada álbum
--comprimento max da letra por algum
with aux as (
select album_id, max(length(lyrics)) as max_len
from Musica
group by album_id
)
--selecionar musicas com esse comprimento
select a.titulo as album, m.titulo as música, length(m.lyrics) as comp_letra
from Album as a join Musica as m on m.album_id = a.id
join aux as x on x.album_id = m.album_id and x.max_len = length(m.lyrics)
order by album;

