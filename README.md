#### initial setup:
installs requirements and run containers.
exposing .env file is a bad practice. but I have nothing to lose here.
```bash
docker-compose up
```

#### navigate to python server container:
```bash
docker-compose exec web sh
```
after you got into container shell execute these:
#### create db schema for jwt and etc:
```bash
python manage.py migrate
```

#### create superuser:
```bash
python manage.py createsuperuser --username admin --email hamed.gk@yahoo.com
```

#### testing:
the postman collection is available in project directory
