# Sanctum Django Setup

### To Run a *Local* Server on Development
1. cd into the project folder
2. Install the **dependencies**
3. Run `cat .env.example > .env` (Or copy it manually if you want)
4. Run `docker compose -f docker-compose.dev.yml up --build` to start the development server
5. To close the containers just run `docker compose -f docker-compose.dev.yml down` 


### To create a superuser to access the django admin panels
1. Once the docker containers are running, exec into the django/backend container `docker exec -it {container_name} bash`
2. Once in the docker container, run `python manage.py createsuperuser`
3. Follow the prompt to create the user
4. Once done you can exit the container with **ctrl-d**
5. To login to admin panel you can go to *BASEURL/admin*

### Env values explanationed
Key|Value
----|----
POSTGRES_DB|Database name
POSTGRES_USER|Database user
POSTGRES_PASSWORD|Database password for user
DB_HOST|Database host for Django to connect to
DB_PORT|Port to connect to the database
DB_NAME|Database name (for django to use)
DB_USER|Database user (for django to use)
DB_PASS||Database password for user (for django to use)
DJANGO_API_KEY|Django secret api key for protected endpoint


### Installing Depencencies for Django (For Developers)
##### For developers if you want to install in your local machine, if you are developing using docker you can ignore this
1. cd into the django/backend folder
2. Run `python3 -m venv env` to create a env
3. Run `source env/bin/activate` to start the env
4. In the same directory as your requirements.txt run `pip install -r requirements.txt`

