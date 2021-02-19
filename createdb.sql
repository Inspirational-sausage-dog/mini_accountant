create table categories(
    id integer primary key,
    user_id integer,
    name varchar (64),
    max_ammount integer
);

create table expenses(
    id integer primary key,
    user_id integer,
    category_id integer,
    ammount integer,
    created datetime,
    FOREIGN KEY(category_id) REFERENCES category(id)
);
