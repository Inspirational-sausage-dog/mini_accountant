# mini_accountant

SQLite база данных будет лежать в папке проекта db/finance.db.

docker build -t tgfinance ./
docker run -d --name tg -v /local_project_path/db:/home/db tgfinance

Чтобы войти в работающий контейнер:

docker exec -ti tg bash
Войти в контейнере в SQL шелл:

docker exec -ti tg bash
sqlite3 /home/db/finance.db
