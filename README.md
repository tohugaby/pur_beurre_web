# PUR BEURRE WEB (pur_beurre_web)


Supported versions of python: **3.4, 3.5, 3.6, 3.7**


## What is Pur Beurre ?

Openclassrooms project 8: Use Open Food Facts database to substitute food products with an healthier one.

A website to find healthier products.


## Getting starded

You need to install Postgresql on your system.


**Pipenv** is used to manage dependencies and virtual environment. 
You need to install pipenv on your system.

```
pip install pipenv
```
In project directory run following command to create virtual environment install dependencies:

```
pipenv install
```


### Writing the settings file

Pur_beurre_web is a django project. So you can override settings with your own settings in pur_beurre_web/settings directorie.

Present "prod.py" settings file is designed for Heroku deployement

#### Custom settings


```python

JSON_DIR_NAME = 'cached_json_files'
JSON_DIR_PATH = os.path.join(BASE_DIR, JSON_DIR_NAME)

```

These 2 settings define where cached data will be stored after getting them from Open Food Facts Api

### Applying migrations

To apply migrations use following command in project directory:

development settings:
```shell
python manage.py migrate
```

production settings:
```shell
DJANGO_SETTINGS_MODULE='pur_beurre_web.settings.prod' python manage.py migrate
```

### Getting data from OpenFoodFacts API with api_to_db command

Collection of data from OpenFoodFacts API is based on **api_to_db** django custom command.

You can see **api_to_db** help by running (in pipenv shell)

Usage:
```python
python manage.py api_to_db --help
```

Open Food Facts provide products per 20 on each page. 
**api_to_db** allows you to specify a start page and a nb of pages to recover.

Usage:
```python
python manage.py api_to_db --start_page 3 --nb_page 5
```

You can also work with cached data from previous recovery to limit api calls.

Usage:
```python
python manage.py api_to_db --start_page 3 --nb_page 5 --from_cache
```

For deployment with limited space for database, there is also a *Grumpy mode* that doesn't insert into db products with missing data like nutrition grade, sodium, sugar...

Usage:
```python
python manage.py api_to_db --start_page 3 --nb_page 5 --from_cache --grumpy_mode
```

**api_to_db** deals easily with connexions failure because it stores last recovered page. When relaunching command after a failure it starts from last recovered page.


### Collecting static files

To collect static files use following commands in project directory (only with production settings):

production settings:
```shell
DJANGO_SETTINGS_MODULE='pur_beurre_web.settings.prod' python manage.py compilescss

DJANGO_SETTINGS_MODULE='pur_beurre_web.settings.prod' python manage.py collectstatic
```

### Launching the program

To launch the program use following command in project directory:

development settings:
```shell
python manage.py runserver
```

production settings:
```shell
DJANGO_SETTINGS_MODULE='pur_beurre_web.settings.prod' python manage.py runserver
```


## Launching the test

To launch unit tests and functionnal tests (using selenium):

```shell
DJANGO_SETTINGS_MODULE='pur_beurre_web.settings.test' python manage.py test
```


### Note
Gecko driver is required for functionnal tests.
Install it from https://github.com/mozilla/geckodriver


## Heroku deployment

Dont forget to change ALLOWED_HOSTS settings in your prod settings.


### Note
Heroku build with django-sass-processor needs specific buildpack:

run in your terminal
```
heroku create --buildpack https://github.com/drpancake/heroku-buildpack-django-sass.git
```

and then:
```
heroku buildpacks:add --index 2 https://github.com/drpancake/heroku-buildpack-django-sass.git
```


## Contributing

This project do not need pull requests because it is part of a learning path. That is why i can't update it after mentor's validation.

## Versioning

I use [SemVer](http://semver.org/) for versioning. 

## Authors

* **Tom Gabrièle**

See also the list of [contributors](https://github.com/tomlemeuch/pur_beurre_web/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/tomlemeuch/pur_beurre_web/blob/master/LICENSE) file for details








