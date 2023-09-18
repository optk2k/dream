FROM python:3.11.5

# в каком каталоге выполнять команды
WORKDIR /dream/
# что копировать с нашей машины в контейнер
COPY ./web_app /dream/

RUN python -m pip install pipenv
RUN pipenv install --system --deploy

# какой скрипт запускать при запуске контейнера
ENTRYPOINT gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
# казываем какой порт мы можем пробросить
EXPOSE 8000
