# Project setup
1. Ensure you have installed `docker` + `docker-compose`
2. Enter project directory
3. Run
```shell
docker-compose up
```
App should be available on `127.0.0.1:8000`
4. (optional) To populate db with exemplary data:
```shell
docker-compose run --rm app python manage.py populate_db
```