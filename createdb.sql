create table categories(
    id integer primary key,
    name varchar (64),
    max_ammount integer
);

create table expenses(
    id integer primary key,
    category_id integer,
    ammount float,
    created datetime,
    FOREIGN KEY(category_id) REFERENCES category(id)
);
