# pur_beurre_web
A website to find healthier products



Note:
Heroku build with django-sass-processor needs specific buildpack:

run in your terminal
```
heroku create --buildpack https://github.com/drpancake/heroku-buildpack-django-sass.git
```

and then:
```
heroku buildpacks:add --index 2 https://github.com/drpancake/heroku-buildpack-django-sass.git
```