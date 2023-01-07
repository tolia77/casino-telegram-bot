create table user_data
(
id serial not null primary key,
username varchar(50) not null,
balance INT not null,
games_played INT not null
)
