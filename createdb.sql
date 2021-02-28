create table categories(
    user_id integer,
    id integer primary key,
    name varchar (64),
    max_ammount integer
);

create table expenses(
    user_id integer,
    id integer primary key,
    category_id integer,
    ammount integer,
    created datetime,
    FOREIGN KEY(category_id) REFERENCES category(id)
);

create table budget(
    user_id integer primary key,
    ammount integer
);
