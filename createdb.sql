create table categories(
    id integer primary key,
    name varchar (64)
);

create table expenses(
    id integer primary key,
    category_id integer,
    ammount integer,
    created datetime,
    FOREIGN KEY(category_id) REFERENCES category(id)
);