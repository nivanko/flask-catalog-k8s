\connect catalog;

create table if not exists category
(
    id   serial primary key,
    name varchar(25) not null
);

create table if not exists users
(
    id       serial primary key,
    username varchar(250) not null,
    fullname varchar(250) not null
);

create table if not exists item
(
    id          serial primary key,
    name        varchar(50) not null,
    description varchar(250),
    picture     varchar(50),
    category_id integer references category(id),
    user_id     integer references users(id)
);

alter table category owner to dbuser;
alter table item owner to dbuser;
alter table users owner to dbuser;

insert into category(name) values ('Backpacks');
insert into category(name) values ('Camp Bedding');
insert into category(name) values ('Camp Kitchen');
insert into category(name) values ('Electronics');
insert into category(name) values ('Gadgets');
insert into category(name) values ('Gear');
insert into category(name) values ('Health');
insert into category(name) values ('Lighting');
insert into category(name) values ('Safety');
insert into category(name) values ('Tents');
insert into category(name) values ('Water');

insert into users(username, fullname) values ('nivanko', 'Nikolay Ivanko');

insert into item(name, description, picture, category_id, user_id)
    select 'Day Pack',
            'A daypack is a smaller, frameless backpack ' ||
            'that can hold enough contents for a day hike, ' ||
            'or a day''s worth of other activities.',
            'daypack.jpg',
            (select id from category where name = 'Backpacks' limit 1),
            (select id from users where username = 'nivanko' limit 1);
