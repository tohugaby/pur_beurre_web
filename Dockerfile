FROM python:3.7

RUN mkdir -p /var/www/src/
WORKDIR /var/www/src/

COPY pur_beurre_web ./pur_beurre_web
COPY static ./static
COPY substitute_finder ./substitute_finder
COPY manage.py Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh
EXPOSE 8000



CMD ./wait-for-it.sh db:5432 -t 0 -- python manage.py collectstatic --noinput \
&& python manage.py migrate \
&& newrelic-admin generate-config $NEW_RELIC_KEY newrelic.ini \
&& NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn pur_beurre_web.wsgi:application -b 0.0.0.0:8000

