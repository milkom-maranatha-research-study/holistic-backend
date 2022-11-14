# holistic-backend

It's a web service project built on top of the Django REST Framework, and its API can be used by the Client or other services.

## Prerequisites
### Docker

All our components run in Docker containers. Development orchestration is handled by _docker-compose_. Therefore, installing Docker on your machine is required. Regarding installation guidelines, please follow the particular links below:

For machines running **MacOS** you can follow steps explained [here](https://docs.docker.com/docker-for-mac/install/)

For machines running **Linux (Ubuntu)** you can follow steps explained [here](https://docs.docker.com/desktop/install/linux-install/)

Please also ensures that _docker-compose_ command is installed.

### How to Start the Project

This project provides a docker-compose file already. Hence, after installing `Docker` and `docker-compose`, you only need to execute this command from the command line.

```bash
$ docker-compose up --build
```
This will build multiple docker images, one per component. In addition, `docker-compose up` runs all containers. One such
container is the ```web```, another one is the ```postgres``` container.

### How to Access the Admin Panel
Django already has a built-in admin site, where we can inspect most of the existing model and activity. To use it, you need to create a superuser first by executing this command.

```bash
$ docker exec -it holistic-backend\_web\_1 python manage.py createsuperuser
```

This command will ask you for some information such as username, email, and password. Once you have provided all the information needed, it will create a new user in the database that you can use to access the admin site from `http://localhost:8080/admin/`

### How to Test

The project's test runner is also run on top of docker, so all you need to do is to call this command.

```bash
$ docker exec -it holistic-backend\_web\_1 python manage.py test
```